# =============================================================================
# blueprints/notifications.py — Notificaciones in-app
#
# Rutas:
#   GET  /notifications/           — Listado de notificaciones del usuario actual
#   POST /notifications/<id>/read  — Marcar una notificación como leída y redirigir
#   POST /notifications/read-all   — Marcar todas las notificaciones como leídas
#
# Las notificaciones se crean desde utils.notify() y utils.notify_staff().
# El badge con el conteo de no leídas se muestra en el navbar (base.html).
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Notification

bp_notifications = Blueprint("notifications", __name__, url_prefix="/notifications")

# Notificaciones por página en el listado
PER_PAGE = 20


# ── Listado de notificaciones ─────────────────────────────────────────────────
@bp_notifications.route("/")
@login_required
def index():
    """
    Muestra todas las notificaciones del usuario autenticado, paginadas.
    Ordenadas de más reciente a más antigua.
    """
    page = request.args.get("page", 1, type=int)
    pagination = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .paginate(page=page, per_page=PER_PAGE, error_out=False)
    )
    return render_template(
        "notifications/index.html",
        notifications=pagination.items,
        pagination=pagination,
    )


# ── Marcar una notificación como leída ────────────────────────────────────────
@bp_notifications.post("/<int:notif_id>/read")
@login_required
def mark_read(notif_id):
    """
    Marca una notificación específica como leída.
    Si tiene un link asociado, redirige a él (ej: al evento aprobado).
    Solo el dueño de la notificación puede marcarla como leída (403 si otro intenta).
    """
    n = Notification.query.get_or_404(notif_id)

    # Verificar que la notificación pertenece al usuario actual
    if n.user_id != current_user.id:
        abort(403)

    n.read = True
    db.session.commit()

    # Redirigir al link de la notificación si existe, sino al listado
    if n.link:
        return redirect(n.link)
    return redirect(url_for("notifications.index"))


# ── Marcar todas como leídas ──────────────────────────────────────────────────
@bp_notifications.post("/read-all")
@login_required
def read_all():
    """
    Marca todas las notificaciones no leídas del usuario actual como leídas.
    Útil para limpiar el badge del navbar de una sola vez.
    """
    Notification.query.filter_by(user_id=current_user.id, read=False).update({"read": True})
    db.session.commit()
    return redirect(url_for("notifications.index"))
