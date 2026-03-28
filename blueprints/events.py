# =============================================================================
# blueprints/events.py — Gestión de eventos de cueca
#
# Rutas públicas/autenticadas:
#   GET/POST /events/new                    — Publicar nuevo evento
#   GET      /events/<id>                   — Ver detalle de evento
#
# Rutas de moderación (moderator | admin):
#   POST     /events/moderate/<id>/<action> — Aprobar o rechazar evento
#   POST     /events/delete/<id>            — Eliminar evento y su imagen
#   GET      /events/admin/moderation       — Dashboard de moderación con filtros
#
# Lógica especial:
#   - Los admins publican eventos con status="approved" directamente (sin moderación).
#   - Los usuarios normales publican con status="pending" y esperan revisión.
#   - Las imágenes se recortan y redimensionan a formato 9:16 (Instagram Story).
# =============================================================================

import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from extensions import db
from models import Event
from forms import EventForm
from utils import notify, notify_staff

bp_events = Blueprint("events", __name__, url_prefix="/events")

# Extensiones de imagen permitidas al subir
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp"}

# Eventos por página en el dashboard de moderación
PER_PAGE = 12


def allowed_file(filename: str) -> bool:
    """Verifica que el archivo tenga una extensión de imagen permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def save_and_standardize(image_storage) -> str:
    """
    Guarda la imagen subida y la redimensiona al formato estándar (1080×1920, 9:16).

    Proceso:
    1. Valida la extensión del archivo.
    2. Genera un nombre único usando timestamp para evitar colisiones.
    3. Abre la imagen con Pillow y la convierte a RGB.
    4. Recorta centrando para mantener la proporción sin deformar.
    5. Redimensiona al tamaño final y guarda como JPEG optimizado.

    Returns:
        Ruta relativa del archivo guardado (ej: "uploads/imagen_1712345678.jpg").

    Raises:
        ValueError: si la imagen no existe o tiene formato no permitido.
    """
    if not image_storage or image_storage.filename == "":
        raise ValueError("Imagen requerida")
    if not allowed_file(image_storage.filename):
        raise ValueError("Formato no permitido. Usa JPG, PNG o WEBP")

    # Generar nombre de archivo seguro y único con timestamp
    filename = secure_filename(image_storage.filename)
    base, _ = os.path.splitext(filename)
    filename = f"{base}_{int(datetime.utcnow().timestamp())}.jpg"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, filename)

    # Dimensiones objetivo desde la configuración (default 1080×1920)
    std_w = current_app.config["IMAGE_STD_WIDTH"]
    std_h = current_app.config["IMAGE_STD_HEIGHT"]

    img = Image.open(image_storage.stream).convert("RGB")

    # Recorte centrado para ajustar la proporción sin deformar la imagen
    target_ratio = std_w / std_h
    orig_w, orig_h = img.size
    orig_ratio = orig_w / orig_h

    if orig_ratio > target_ratio:
        # Imagen más ancha que el target: recortar los lados
        new_w = int(orig_h * target_ratio)
        left = (orig_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, orig_h))
    else:
        # Imagen más alta que el target: recortar arriba y abajo
        new_h = int(orig_w / target_ratio)
        top = (orig_h - new_h) // 2
        img = img.crop((0, top, orig_w, top + new_h))

    # Redimensionar al tamaño final con filtro de alta calidad
    img = img.resize((std_w, std_h), Image.LANCZOS)

    # Guardar como JPEG con compresión optimizada (quality=85 es buen balance)
    img.save(full_path, format="JPEG", quality=85, optimize=True)

    return f"uploads/{filename}"


# ── Crear evento ──────────────────────────────────────────────────────────────
@bp_events.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """
    Formulario para publicar un nuevo evento de cueca.

    Comportamiento según rol:
      - Admin:   el evento se aprueba automáticamente (status="approved"),
                 visible al público de inmediato sin pasar por moderación.
      - Usuario: el evento queda pendiente (status="pending") y se notifica
                 al staff para revisión.

    Las opciones de 'comuna' se cargan por JS según la región; se inyectan
    manualmente antes de validar para que WTForms no las rechace.
    """
    form = EventForm()

    # Inyectar la opción de comuna enviada por JS para que pase la validación de WTForms
    if form.is_submitted() and not form.comuna.choices:
        selected = (request.form.get("comuna") or "").strip()
        if selected:
            form.comuna.choices = [(selected, selected)]

    if form.validate_on_submit():
        try:
            image_path = save_and_standardize(form.image.data)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("events/new.html", form=form)

        bases   = form.bases_url.data.strip()   if form.bases_url.data   else None
        contact = form.contact_info.data.strip() if form.contact_info.data else None
        end_dt  = form.end_date.data             if form.end_date.data    else None

        # Los admins publican directamente; el resto pasa por moderación
        is_admin = current_user.role == "admin"
        status   = "approved" if is_admin else "pending"

        e = Event(
            title=form.title.data.strip(),
            kind=form.kind.data,
            date=form.date.data,
            end_date=end_dt,
            region=form.region.data,
            comuna=form.comuna.data,
            place=form.place.data.strip(),
            description=form.description.data.strip(),
            contact_info=contact,
            bases_url=bases,
            image_path=image_path,
            user_id=current_user.id,
            status=status,
        )
        db.session.add(e)
        db.session.flush()  # obtener e.id antes del commit para usar en el link

        if is_admin:
            # Admin: publicación directa, sin notificar al staff
            flash("Evento publicado correctamente.", "success")
        else:
            # Usuario normal: notificar al staff para revisión
            notify_staff(
                f"Nuevo evento pendiente: «{e.title}» de {current_user.name}.",
                link=url_for("events.show", event_id=e.id),
            )
            flash("Evento enviado a revisión. Te notificaremos cuando sea aprobado.", "success")

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("events/new.html", form=form)


# ── Moderar evento ────────────────────────────────────────────────────────────
@bp_events.route("/moderate/<int:event_id>/<action>", methods=["POST"])
@login_required
def moderate(event_id, action):
    """
    Aprueba o rechaza un evento pendiente.
    Solo accesible para moderadores y admins.
    Notifica al autor del evento sobre el resultado.

    Actions válidas: "approve" | "reject"
    """
    if current_user.role not in ("moderator", "admin"):
        abort(403)

    event = Event.query.get_or_404(event_id)

    if action == "approve":
        event.status  = "approved"
        event.expired = False  # asegurar que no esté marcado como expirado
        notify(
            event.user_id,
            f"Tu evento «{event.title}» ha sido aprobado y ya es visible.",
            link=url_for("events.show", event_id=event.id),
        )
        flash("Evento aprobado.", "success")

    elif action == "reject":
        event.status = "rejected"
        notify(
            event.user_id,
            f"Tu evento «{event.title}» fue rechazado. Contáctate con un moderador.",
            link=url_for("events.show", event_id=event.id),
        )
        flash("Evento rechazado.", "warning")

    else:
        abort(400)  # acción desconocida

    db.session.commit()
    # Volver a la página anterior (dashboard de moderación) o al dashboard por defecto
    return redirect(request.referrer or url_for("events.moderation_dashboard"))


# ── Eliminar evento ───────────────────────────────────────────────────────────
@bp_events.route("/delete/<int:event_id>", methods=["POST"])
@login_required
def delete(event_id):
    """
    Elimina un evento de la BD y su imagen del sistema de archivos.
    Solo accesible para moderadores y admins.
    Si el archivo de imagen no existe, continúa sin error.
    """
    if current_user.role not in ("moderator", "admin"):
        abort(403)

    event = Event.query.get_or_404(event_id)

    # Intentar eliminar la imagen física; ignorar si no existe o hay error de permisos
    try:
        img_full = os.path.join(current_app.root_path, "static", event.image_path)
        if os.path.exists(img_full):
            os.remove(img_full)
    except Exception:
        pass  # no bloquear el flujo si falla la eliminación del archivo

    db.session.delete(event)
    db.session.commit()
    flash("Evento eliminado.", "info")
    return redirect(url_for("events.moderation_dashboard"))


# ── Dashboard de moderación ───────────────────────────────────────────────────
@bp_events.route("/admin/moderation")
@login_required
def moderation_dashboard():
    """
    Panel de revisión de eventos para moderadores y admins.
    Permite filtrar por:
      - Texto libre (?q=): busca en título, región, comuna y tipo
      - Estado (?status=): pending | approved | rejected | expired
    Pagina los resultados ordenados por fecha de creación (más nuevos primero).
    """
    if current_user.role not in ("moderator", "admin"):
        abort(403)

    q      = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "pending")
    page   = request.args.get("page", 1, type=int)

    query = Event.query

    # Filtrar por estado/expiración
    if status == "expired":
        query = query.filter_by(expired=True)
    elif status:
        query = query.filter_by(status=status, expired=False)

    # Filtro de búsqueda libre (case-insensitive)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Event.title.ilike(like))
            | (Event.region.ilike(like))
            | (Event.comuna.ilike(like))
            | (Event.kind.ilike(like))
        )

    pagination = query.order_by(Event.created_at.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False
    )
    return render_template(
        "events/moderation.html",
        events=pagination.items,
        pagination=pagination,
        q=q,
        status=status,
    )


# ── Detalle de evento ─────────────────────────────────────────────────────────
@bp_events.route("/<int:event_id>")
def show(event_id):
    """
    Muestra el detalle de un evento.
    Reglas de visibilidad:
      - Eventos aprobados: visibles para todos (incluso no autenticados).
      - Eventos pendientes/rechazados: solo visibles para el autor y para staff.
      - En cualquier otro caso: 404.
    """
    e = Event.query.get_or_404(event_id)

    can_view = e.status == "approved"
    if not can_view and current_user.is_authenticated:
        if current_user.id == e.user_id or current_user.role in ("moderator", "admin"):
            can_view = True

    if not can_view:
        abort(404)

    return render_template("events/show.html", e=e)
