# =============================================================================
# extensions.py — Instancias de extensiones Flask (sin contexto de aplicación)
#
# Las extensiones se instancian aquí sin parámetros para evitar importaciones
# circulares. Cada una se inicializa después con `.init_app(app)` dentro de
# la fábrica create_app() en app.py.
#
# Patrón estándar de Flask para proyectos con Application Factory.
# =============================================================================

from flask_sqlalchemy import SQLAlchemy    # ORM y gestión de conexiones a BD
from flask_login import LoginManager      # Manejo de sesiones y autenticación de usuarios
from flask_migrate import Migrate         # Migraciones de esquema BD con Alembic
from flask_apscheduler import APScheduler # Tareas programadas (cron jobs dentro del proceso)

# Base de datos: PostgreSQL en producción, SQLite en desarrollo local
db = SQLAlchemy()

# Login: controla quién está autenticado, protege rutas con @login_required
login_manager = LoginManager()

# Migrate: permite `flask db migrate` y `flask db upgrade` para evolucionar el esquema
migrate = Migrate()

# Scheduler: ejecuta tareas en background (ej: marcar eventos expirados a las 2 AM)
scheduler = APScheduler()
