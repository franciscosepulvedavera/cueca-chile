# =============================================================================
# app.py — Fábrica de la aplicación Flask (Application Factory Pattern)
#
# Crea y configura la instancia de Flask, registra extensiones, blueprints
# y define la ruta raíz con filtros de categoría y paginación.
# También inicializa APScheduler para la tarea diaria de expiración de eventos.
#
# Uso:
#   flask run          → modo desarrollo
#   python app.py      → inicio directo (debug=True)
# =============================================================================

import os
from datetime import date
from flask import Flask, render_template, request, url_for, Response
from config import Config
from extensions import db, login_manager, migrate, scheduler
from models import Event, User

# ── Importación de todos los blueprints del proyecto ──────────────────────────
from blueprints.auth import bp_auth                      # Registro, login, logout
from blueprints.events import bp_events                  # CRUD de eventos + moderación
from blueprints.admin import bp_admin                    # Panel de administración completo
from blueprints.notifications import bp_notifications    # Notificaciones in-app
from blueprints.championships import bp_championships    # Campeonatos nacionales (público)
from blueprints.creators import bp_creators              # Creadores de contenido (público)
from blueprints.stores import bp_stores                  # Tiendas de cueca (público)
from blueprints.results import bp_results                # Tabla de resultados por región (público)
from blueprints.musicians import bp_musicians               # Músicos y agrupaciones (público)

# Número de eventos por página en el listado principal
PER_PAGE = 12


def create_app():
    """
    Application Factory: crea y devuelve la instancia configurada de Flask.
    Se usa este patrón para facilitar testing y múltiples configuraciones.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Inicialización de extensiones ─────────────────────────────────────────
    db.init_app(app)             # SQLAlchemy: ORM y conexión a PostgreSQL
    migrate.init_app(app, db)    # Flask-Migrate: migraciones Alembic
    login_manager.init_app(app)  # Flask-Login: gestión de sesiones de usuario
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"

    # ── Cloudinary: inicializar si la variable de entorno está configurada ─────
    cloudinary_url = os.getenv("CLOUDINARY_URL", "")
    if cloudinary_url:
        import cloudinary
        # Parsear manualmente la URL: cloudinary://api_key:api_secret@cloud_name
        try:
            rest = cloudinary_url.replace("cloudinary://", "")
            credentials, cloud_name = rest.rsplit("@", 1)
            api_key, api_secret = credentials.split(":", 1)
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
        except Exception:
            # Fallback: dejar que cloudinary lea la variable de entorno directamente
            cloudinary.config(cloudinary_url=cloudinary_url)

    # ── Helper global de imágenes: resuelve URLs locales y de Cloudinary ──────
    @app.template_global()
    def img_url(path: str | None) -> str | None:
        """
        Retorna la URL correcta de una imagen sin importar dónde esté almacenada.
        - Si es una URL completa (Cloudinary/S3): la devuelve tal cual.
        - Si es una ruta relativa local (uploads/...): genera la URL estática.
        - Si es None: devuelve None (los templates muestran el placeholder).
        """
        if not path:
            return None
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return url_for("static", filename=path)

    # ── Registro de blueprints ────────────────────────────────────────────────
    app.register_blueprint(bp_auth)            # /auth/...
    app.register_blueprint(bp_events)          # /events/...
    app.register_blueprint(bp_admin)           # /admin/...
    app.register_blueprint(bp_notifications)   # /notifications/...
    app.register_blueprint(bp_championships)   # /campeonatos/...
    app.register_blueprint(bp_creators)        # /creadores/...
    app.register_blueprint(bp_stores)          # /tiendas/...
    app.register_blueprint(bp_results)         # /resultados/...
    app.register_blueprint(bp_musicians)       # /musicos/...

    # ── Tarea programada: expirar eventos pasados ─────────────────────────────
    # Se ejecuta todos los días a las 2:00 AM (hora de Santiago).
    # Marca como `expired=True` los eventos aprobados cuya fecha ya pasó
    # y notifica al staff para revisión/limpieza manual.
    @scheduler.task("cron", id="expire_events", hour=2, minute=0)
    def expire_past_events():
        with app.app_context():
            from utils import notify_staff
            today = date.today()

            # Buscar eventos aprobados con fecha pasada que aún no estén marcados
            stale = Event.query.filter(
                Event.status == "approved",
                Event.expired == False,
                Event.date < today,
            ).all()

            if not stale:
                return  # Nada que expirar hoy

            for ev in stale:
                ev.expired = True  # Ocultar del listado público

            # Notificar al staff para limpieza manual
            notify_staff(
                f"{len(stale)} evento(s) han expirado y requieren revisión.",
                link="/events/admin/moderation?status=expired",
            )
            db.session.commit()

    # Iniciar el scheduler después de registrar todas las tareas
    scheduler.init_app(app)
    scheduler.start()

    # ── Ruta principal (homepage) ─────────────────────────────────────────────
    # Muestra todos los eventos aprobados y no expirados.
    # Soporta filtro por categoría (?kind=) y paginación (?page=).
    @app.route("/")
    def index():
        kind = request.args.get("kind", "").strip()
        page = request.args.get("page", 1, type=int)

        # Consulta base: solo eventos visibles al público
        query = Event.query.filter_by(status="approved", expired=False)

        # Aplicar filtro de categoría si se especifica
        if kind:
            query = query.filter_by(kind=kind)

        # Ordenar por fecha más próxima primero
        query = query.order_by(Event.date.asc())

        # Paginar resultados
        pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

        # Categorías disponibles para el filtro en la UI
        kinds = ["Nacionales", "Regionales", "Abiertos/Masivos", "Cuecazos", "Benéfico"]

        return render_template(
            "index.html",
            events=pagination.items,
            pagination=pagination,
            kinds=kinds,
            active_kind=kind,
        )

    # ── SEO: sitemap.xml dinámico ─────────────────────────────────────────
    @app.route("/sitemap.xml")
    def sitemap():
        from models import Championship
        base = request.url_root.rstrip("/")
        urls = [
            {"loc": base + "/",                  "changefreq": "daily",   "priority": "1.0"},
            {"loc": base + "/campeonatos/",       "changefreq": "weekly",  "priority": "0.9"},
            {"loc": base + "/resultados/",        "changefreq": "weekly",  "priority": "0.8"},
            {"loc": base + "/musicos/",           "changefreq": "weekly",  "priority": "0.8"},
            {"loc": base + "/creadores/",         "changefreq": "weekly",  "priority": "0.7"},
            {"loc": base + "/tiendas/",           "changefreq": "monthly", "priority": "0.7"},
        ]
        # Agregar URL de cada campeonato individual
        with app.app_context():
            for c in Championship.query.filter_by(active=True).all():
                urls.append({
                    "loc": base + f"/campeonatos/{c.id}",
                    "changefreq": "monthly",
                    "priority": "0.6",
                })
        xml = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for u in urls:
            xml.append(
                f'  <url><loc>{u["loc"]}</loc>'
                f'<changefreq>{u["changefreq"]}</changefreq>'
                f'<priority>{u["priority"]}</priority></url>'
            )
        xml.append("</urlset>")
        return Response("\n".join(xml), mimetype="application/xml")

    # ── SEO: robots.txt ───────────────────────────────────────────────────
    @app.route("/robots.txt")
    def robots():
        base = request.url_root.rstrip("/")
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            "Disallow: /auth/\n"
            "Disallow: /notifications/\n"
            f"Sitemap: {base}/sitemap.xml\n"
        )
        return Response(content, mimetype="text/plain")

    return app


# Punto de entrada para desarrollo local directo
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
