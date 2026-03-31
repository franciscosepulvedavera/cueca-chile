# =============================================================================
# blueprints/results.py — Tabla de Resultados por Región (vista pública)
#
# Rutas:
#   GET /resultados/  — Tabla con conteo de 1°/2°/3° lugares por región
#
# Los datos se calculan en tiempo real desde la tabla HonorEntry.
# Todas las 16 regiones de Chile aparecen siempre, incluso si tienen 0 resultados.
# El orden es Norte→Sur según la constante REGIONES de forms.py.
# =============================================================================

from flask import Blueprint, render_template, request
from sqlalchemy import func, distinct
from extensions import db
from models import HonorEntry
from forms import REGIONES

bp_results = Blueprint("results", __name__, url_prefix="/resultados")

REGION_ORDER = [r[0] for r in REGIONES]


@bp_results.route("/")
def index():
    """
    Tabla de resultados por región, filtrable por año.
    ?year=YYYY muestra solo ese año. Sin parámetro muestra todos los años.
    position=0 (pareja popular) se excluye — solo posiciones competitivas 1-4.
    """
    # Años disponibles (para mostrar el selector)
    available_years = [
        r[0] for r in (
            db.session.query(distinct(HonorEntry.year))
            .filter(HonorEntry.position > 0)
            .order_by(HonorEntry.year.desc())
            .all()
        )
    ]

    # Año seleccionado (None = todos)
    selected_year = request.args.get("year", type=int)
    if selected_year and selected_year not in available_years:
        selected_year = None

    query = (
        db.session.query(
            HonorEntry.region,
            HonorEntry.position,
            func.count(HonorEntry.id).label("total"),
        )
        .filter(HonorEntry.position > 0)  # excluye pareja popular
    )
    if selected_year:
        query = query.filter(HonorEntry.year == selected_year)

    rows = query.group_by(HonorEntry.region, HonorEntry.position).all()

    data: dict = {r: {} for r in REGION_ORDER}
    for region, position, total in rows:
        if region in data:
            data[region][position] = total

    table = [{"region": r, "counts": data[r]} for r in REGION_ORDER]

    return render_template(
        "results/index.html",
        table=table,
        available_years=available_years,
        selected_year=selected_year,
    )
