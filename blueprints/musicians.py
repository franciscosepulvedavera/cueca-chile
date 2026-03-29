# =============================================================================
# blueprints/musicians.py — Directorio público de músicos y agrupaciones
# =============================================================================

from flask import Blueprint, render_template
from models import Musician

bp_musicians = Blueprint("musicians", __name__, url_prefix="/musicos")


@bp_musicians.route("/")
def index():
    """Directorio público de músicos y agrupaciones activos."""
    items = Musician.query.filter_by(active=True).order_by(Musician.name.asc()).all()
    return render_template("musicians/index.html", musicians=items)
