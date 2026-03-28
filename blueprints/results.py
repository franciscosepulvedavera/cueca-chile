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

from flask import Blueprint, render_template
from sqlalchemy import func
from extensions import db
from models import HonorEntry
from forms import REGIONES

bp_results = Blueprint("results", __name__, url_prefix="/resultados")

# Orden oficial Norte→Sur, extraído de la lista REGIONES de forms.py
# Se usa para mantener el orden geográfico en la tabla aunque no haya datos.
REGION_ORDER = [r[0] for r in REGIONES]


# ── Tabla de resultados por región ────────────────────────────────────────────
@bp_results.route("/")
def index():
    """
    Muestra la tabla de resultados acumulados por región de Chile.

    Proceso:
    1. Agrupa todas las HonorEntry por (region, position) y cuenta cuántas hay.
    2. Construye un dict {region: {1: n_primeros, 2: n_segundos, 3: n_terceros}}.
    3. Genera la lista final en orden Norte→Sur, incluyendo regiones con 0 resultados.

    La plantilla results/index.html muestra "—" para las celdas con valor 0.
    """
    # Consulta SQL equivalente a:
    # SELECT region, position, COUNT(*) FROM honor_entry GROUP BY region, position
    rows = (
        db.session.query(
            HonorEntry.region,
            HonorEntry.position,
            func.count(HonorEntry.id).label("total"),
        )
        .group_by(HonorEntry.region, HonorEntry.position)
        .all()
    )

    # Inicializar el dict con todas las regiones (dict vacío = sin resultados)
    data: dict = {r: {} for r in REGION_ORDER}

    # Poblar el dict con los conteos obtenidos de la BD
    for region, position, total in rows:
        if region in data:
            data[region][position] = total

    # Convertir a lista ordenada Norte→Sur para la plantilla
    table = [
        {"region": r, "counts": data[r]}
        for r in REGION_ORDER
    ]

    return render_template("results/index.html", table=table)
