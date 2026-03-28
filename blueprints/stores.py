# =============================================================================
# blueprints/stores.py — Tiendas (vista pública)
#
# Rutas:
#   GET /tiendas/  — Directorio de tiendas activas
#
# Solo tiendas con `active=True` son visibles al público.
# La gestión (crear/editar/eliminar) se hace desde el panel admin.
# =============================================================================

from flask import Blueprint, render_template
from models import Store

bp_stores = Blueprint("stores", __name__, url_prefix="/tiendas")


# ── Directorio público de tiendas ─────────────────────────────────────────────
@bp_stores.route("/")
def index():
    """
    Muestra el directorio de tiendas especializadas en cueca activas,
    ordenadas alfabéticamente. Cada tarjeta incluye nombre, descripción,
    imagen y link a la tienda.
    """
    items = Store.query.filter_by(active=True).order_by(Store.name.asc()).all()
    return render_template("stores/index.html", stores=items)
