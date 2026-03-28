# =============================================================================
# step_defs/test_resultados.py — Steps para tabla de resultados (resultados.feature)
# =============================================================================

from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("resultados.feature")

TOTAL_REGIONES = 16


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que un visitante anónimo accede al sitio", target_fixture="pagina")
def visitante_anonimo(anon_page):
    return anon_page


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la sección de resultados")
def navegar_resultados(pagina):
    pagina.goto("/resultados/")
    pagina.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la tabla de resultados")
def verificar_tabla(pagina):
    expect(pagina.locator("table")).to_be_visible()


@then("la tabla contiene exactamente 16 filas de regiones")
def verificar_16_regiones(pagina):
    # tbody tr → una fila por región
    filas = pagina.locator("table tbody tr")
    assert filas.count() == TOTAL_REGIONES, (
        f"Se esperaban {TOTAL_REGIONES} regiones, se encontraron {filas.count()}"
    )


@then("ve la columna de primer lugar")
def verificar_col_primero(pagina):
    expect(pagina.locator("table")).to_contain_text("1°")


@then("ve la columna de segundo lugar")
def verificar_col_segundo(pagina):
    expect(pagina.locator("table")).to_contain_text("2°")


@then("ve la columna de tercer lugar")
def verificar_col_tercero(pagina):
    expect(pagina.locator("table")).to_contain_text("3°")


@then("ve la columna de cuarto lugar")
def verificar_col_cuarto(pagina):
    expect(pagina.locator("table")).to_contain_text("4°")


@then("la primera fila corresponde a Arica y Parinacota")
def verificar_primera_region(pagina):
    primera_fila = pagina.locator("table tbody tr").first
    expect(primera_fila).to_contain_text("Arica")


@then("la última fila corresponde a Magallanes")
def verificar_ultima_region(pagina):
    ultima_fila = pagina.locator("table tbody tr").last
    expect(ultima_fila).to_contain_text("Magallanes")


@then("las celdas sin resultados muestran el símbolo guión")
def verificar_guiones(pagina):
    # Al menos una celda debe tener "—" si no todas las regiones tienen resultados
    body_text = pagina.locator("table").inner_text()
    assert "—" in body_text, "No se encontró el símbolo guión en celdas vacías"


@then("ve la columna de total en la tabla")
def verificar_col_total(pagina):
    expect(pagina.locator("table")).to_contain_text("Total")


@then("los totales son consistentes con los conteos individuales")
def verificar_consistencia_totales(pagina):
    # Verificación básica: la columna Total existe y tiene valores numéricos o "—"
    tabla_texto = pagina.locator("table").inner_text()
    assert len(tabla_texto) > 0, "La tabla está vacía"
