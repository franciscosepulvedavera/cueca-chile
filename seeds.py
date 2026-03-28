# =============================================================================
# seeds.py — Script de inicialización de datos base
#
# Crea el usuario administrador inicial en la base de datos.
# Lee las credenciales desde variables de entorno (.env) para no hardcodear
# datos sensibles en el código fuente.
#
# Uso:
#   python seeds.py
#
# Variables requeridas en .env:
#   ADMIN_EMAIL     — email del administrador (ej: admin@tusitio.cl)
#   ADMIN_PASSWORD  — contraseña (mínimo 6 caracteres)
#   ADMIN_NAME      — nombre visible (opcional, default: "Administrador")
# =============================================================================

import os
from dotenv import load_dotenv
from app import create_app
from extensions import db
from models import User

# Cargar variables de entorno desde .env antes de leerlas
load_dotenv()


def seed_admin():
    """
    Crea el usuario administrador inicial si no existe.
    Si ya hay un usuario con el mismo email, no hace nada (idempotente).
    """
    app = create_app()
    with app.app_context():
        # Leer credenciales del entorno
        admin_email    = os.environ.get("ADMIN_EMAIL")
        admin_password = os.environ.get("ADMIN_PASSWORD")
        admin_name     = os.environ.get("ADMIN_NAME", "Administrador")

        # Validar que las variables obligatorias estén definidas
        if not admin_email or not admin_password:
            print("❌ Define ADMIN_EMAIL y ADMIN_PASSWORD en tu archivo .env antes de ejecutar seeds.")
            return

        # Verificar si ya existe un usuario con ese email (operación idempotente)
        existing = User.query.filter_by(email=admin_email.lower()).first()
        if existing:
            print(f"⚠️  Ya existe un usuario con el email {admin_email}.")
            return

        # Crear el usuario administrador
        admin = User(
            name=admin_name,
            email=admin_email.lower(),
            role="admin",   # acceso completo al panel de administración
            banned=False,
        )
        admin.set_password(admin_password)  # hashear contraseña con PBKDF2-SHA256
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Administrador creado: {admin_email}")


# Punto de entrada al ejecutar el script directamente
if __name__ == "__main__":
    seed_admin()
