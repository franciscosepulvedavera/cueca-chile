# =============================================================================
# blueprints/championships.py — Campeonatos Nacionales (vista pública)
#
# Rutas:
#   GET /campeonatos/       — Lista de campeonatos activos
#   GET /campeonatos/<id>   — Detalle del campeonato + cuadro de honor filtrado por año
#
# Solo campeonatos con `active=True` son visibles al público.
# La gestión (crear/editar/eliminar) se hace desde el panel admin.
# =============================================================================

from flask import Blueprint, render_template, request, abort
from models import Championship, HonorEntry

bp_championships = Blueprint("championships", __name__, url_prefix="/campeonatos")


# ── Listado público de campeonatos ────────────────────────────────────────────
@bp_championships.route("/")
def index():
    """
    Muestra todos los campeonatos activos ordenados alfabéticamente.
    Cada tarjeta enlaza al detalle del campeonato con su cuadro de honor.
    """
    items = Championship.query.filter_by(active=True).order_by(Championship.name.asc()).all()
    return render_template("championships/index.html", championships=items)


# ── Detalle de un campeonato ──────────────────────────────────────────────────
@bp_championships.route("/<int:champ_id>")
def show(champ_id):
    """
    Muestra el detalle de un campeonato y su cuadro de honor.

    El cuadro de honor se filtra por año (?year=YYYY).
    Si no se especifica año, se muestra el más reciente con entradas.
    Las entradas se ordenan por categoría y posición (1°→2°→3°).

    Retorna 404 si el campeonato no existe o no está activo.
    """
    champ = Championship.query.get_or_404(champ_id)

    # Solo mostrar campeonatos activos al público
    if not champ.active:
        abort(404)

    # Años disponibles (el model los retorna ordenados desc)
    years = champ.years()

    # Año seleccionado por parámetro; si no se indica, usar el más reciente
    selected_year = request.args.get("year", type=int)
    if not selected_year and years:
        selected_year = years[0]

    # Cargar entradas del año seleccionado, ordenadas por categoría y posición
    entries = []
    if selected_year:
        entries = (
            HonorEntry.query
            .filter_by(championship_id=champ.id, year=selected_year)
            .order_by(HonorEntry.category.asc(), HonorEntry.position.asc())
            .all()
        )

    return render_template(
        "championships/show.html",
        champ=champ,
        years=years,
        selected_year=selected_year,
        entries=entries,
    )
