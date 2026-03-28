# =============================================================================
# blueprints/creators.py — Creadores de Contenido (vista pública)
#
# Rutas:
#   GET /creadores/  — Directorio de creadores de contenido activos
#
# Solo creadores con `active=True` son visibles al público.
# La gestión (crear/editar/eliminar) se hace desde el panel admin.
# =============================================================================

from flask import Blueprint, render_template
from models import ContentCreator

bp_creators = Blueprint("creators", __name__, url_prefix="/creadores")


# ── Directorio público de creadores ──────────────────────────────────────────
@bp_creators.route("/")
def index():
    """
    Muestra el directorio de creadores de contenido de cueca activos,
    ordenados alfabéticamente. Cada tarjeta incluye nombre, descripción,
    imagen y link al canal o perfil.
    """
    items = ContentCreator.query.filter_by(active=True).order_by(ContentCreator.name.asc()).all()
    return render_template("creators/index.html", creators=items)
