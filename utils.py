# =============================================================================
# utils.py — Funciones utilitarias compartidas
#
# Provee helpers para crear notificaciones in-app sin duplicar lógica
# en los diferentes blueprints.
#
# Importante: las funciones aquí NO hacen db.session.commit().
# El commit se delega al caller para que sea parte de la misma transacción.
# =============================================================================

from extensions import db
from models import Notification, User


def notify(user_id: int, message: str, link: str = None) -> None:
    """
    Crea una notificación in-app para un usuario específico.

    Args:
        user_id: ID del usuario destinatario.
        message: Texto de la notificación (máx. 500 caracteres).
        link:    URL opcional a la que se redirige al hacer click en la notificación.

    Nota: no hace commit. El caller debe llamar db.session.commit()
    junto con el resto de su operación principal.
    """
    n = Notification(user_id=user_id, message=message, link=link)
    db.session.add(n)


def notify_staff(message: str, link: str = None) -> None:
    """
    Envía una notificación a todos los moderadores y administradores activos.

    Usado para alertar al equipo de moderación sobre eventos pendientes,
    eventos expirados u otras situaciones que requieren atención.
    Solo notifica a usuarios no baneados con rol moderator o admin.

    Args:
        message: Texto de la notificación.
        link:    URL opcional de destino al leer la notificación.
    """
    # Obtener todos los miembros del staff activos (no baneados)
    staff = User.query.filter(
        User.role.in_(["moderator", "admin"]),
        User.banned == False,
    ).all()

    # Crear una notificación individual para cada uno
    for u in staff:
        notify(u.id, message, link)
