# =============================================================================
# config.py — Configuración centralizada de la aplicación Flask
#
# Carga variables desde el archivo .env (via python-dotenv) y expone
# la clase Config que se pasa a Flask en create_app().
#
# Variables en .env:
#   SECRET_KEY        — clave para firmar cookies y tokens CSRF (obligatorio en prod)
#   DATABASE_URL      — URI de conexión a PostgreSQL (o sqlite:/// en dev)
#   IMAGE_STD_WIDTH   — ancho de imagen estándar en px (default: 1080)
#   IMAGE_STD_HEIGHT  — alto de imagen estándar en px  (default: 1920)
#   ADMIN_EMAIL       — email del admin inicial (usado en seeds.py)
#   ADMIN_PASSWORD    — contraseña del admin inicial (usado en seeds.py)
#   ADMIN_NAME        — nombre del admin inicial (default: "Administrador")
# =============================================================================

from datetime import timedelta
import os
from dotenv import load_dotenv

# Cargar el archivo .env antes de leer cualquier variable de entorno
load_dotenv()


class Config:
    # ── Seguridad ─────────────────────────────────────────────────────────────
    # SECRET_KEY firma las cookies de sesión y los tokens CSRF de Flask-WTF.
    # En producción DEBE definirse en .env con un valor largo y aleatorio.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # ── Base de datos ─────────────────────────────────────────────────────────
    # Producción: postgresql://user:pass@host:port/dbname
    # Desarrollo: sqlite:///cueca.db
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///cueca.db")
    # Deshabilitar señales de modificación de SQLAlchemy (mejora rendimiento)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Sesiones ──────────────────────────────────────────────────────────────
    # Duración de la cookie "recuérdame" al usar login_user(remember=True)
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    # ── Subida de archivos ────────────────────────────────────────────────────
    # Directorio donde se guardan las imágenes subidas (eventos, campeonatos, etc.)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # Límite de 10 MB por archivo subido

    # ── Formato de imagen estándar: Historia de Instagram (9:16) ─────────────
    # Los eventos recortan y redimensionan la imagen a este tamaño al subir.
    # Se puede sobrescribir en .env para otros formatos.
    IMAGE_STD_WIDTH  = int(os.environ.get("IMAGE_STD_WIDTH",  1080))
    IMAGE_STD_HEIGHT = int(os.environ.get("IMAGE_STD_HEIGHT", 1920))

    # ── APScheduler ───────────────────────────────────────────────────────────
    # No exponer la API REST del scheduler (no se necesita endpoint público)
    SCHEDULER_API_ENABLED = False
    # Zona horaria para las tareas cron (expira eventos a las 2 AM Santiago)
    SCHEDULER_TIMEZONE = "America/Santiago"
