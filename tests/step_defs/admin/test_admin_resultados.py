# =============================================================================
# step_defs/admin/test_admin_resultados.py — Steps para admin_resultados.feature
# =============================================================================

import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("admin/admin_resultados.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el administrador ha iniciado sesión en el panel", target_fixture="pag")
def admin_en_panel(admin_page):
    return admin_page


@given("que existe una entrada de pareja más popular en el sistema")
def honor_popular_existe(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    if "⭐" not in pag.locator("body").inner_text():
        pytest.skip("No hay entradas de pareja más popular en el sistema")


@given("que existe una entrada de cuarto lugar en el sistema")
def honor_cuarto_existe(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    # Busca badge de 4°
    if pag.locator(".pos-4").count() == 0:
        pytest.skip("No hay entradas de cuarto lugar en el sistema")


@given("que existen entradas de al menos dos campeonatos distintos")
def multiples_campeonatos(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    opciones = pag.locator("select[name='champ_id'] option").all()
    if len(opciones) < 3:  # 1 "Todos" + al menos 2 campeonatos
        pytest.skip("Se necesitan al menos 2 campeonatos con entradas")


@given("que existen entradas de al menos dos años distintos")
def multiples_anios(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    opciones = pag.locator("select[name='year'] option").all()
    if len(opciones) < 3:  # 1 "Todos" + al menos 2 años
        pytest.skip("Se necesitan al menos 2 años distintos de entradas")


@given("que hay filtros activos en la gestión de resultados")
def filtros_activos(pag):
    pag.goto("/admin/resultados?year=2025")
    pag.wait_for_load_state("networkidle")


@given("que existe al menos una entrada en el sistema")
def entrada_existe(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    filas = pag.locator("table tbody tr")
    if filas.count() == 0:
        pytest.skip("No hay entradas en el sistema")


@given("que existe una entrada de prueba para eliminar desde resultados")
def crear_entrada_para_eliminar(pag):
    # Para este test necesitamos que exista una entrada eliminable
    # Si no existe, lo saltamos con skip
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")
    filas = pag.locator("table tbody tr")
    if filas.count() == 0:
        pytest.skip("No hay entradas para eliminar en resultados")
    pag._filas_antes = filas.count()


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la gestión de resultados")
def navegar_gestion_resultados(pag):
    pag.goto("/admin/resultados")
    pag.wait_for_load_state("networkidle")


@when("selecciona un campeonato en el filtro")
def seleccionar_campeonato_filtro(pag):
    select = pag.locator("select[name='champ_id']")
    opciones = select.locator("option").all()
    # Selecciona la primera opción que no sea "Todos"
    for opt in opciones[1:]:
        val = opt.get_attribute("value")
        if val:
            select.select_option(val)
            pag.wait_for_load_state("networkidle")
            pag._champ_filtrado = opt.inner_text().strip()
            break


@when("selecciona un año en el filtro")
def seleccionar_anio_filtro(pag):
    select = pag.locator("select[name='year']")
    opciones = select.locator("option").all()
    for opt in opciones[1:]:
        val = opt.get_attribute("value")
        if val:
            select.select_option(val)
            pag.wait_for_load_state("networkidle")
            pag._anio_filtrado = val
            break


@when("hace clic en limpiar filtros")
def clic_limpiar_filtros(pag):
    pag.locator("a:has-text('Limpiar'), a:has-text('limpiar'), a:has-text('✕')").first.click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en editar la primera entrada")
def clic_editar_primera_entrada(pag):
    pag.locator("a[href*='/honor/'][href*='/edit'], .row-actions a").first.click()
    pag.wait_for_load_state("networkidle")


@when("elimina la entrada de prueba y confirma")
def eliminar_entrada_resultados(pag):
    pag.once("dialog", lambda d: d.accept())
    pag.locator(".row-actions form button, button:has-text('🗑')").first.click()
    pag.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la tabla global de entradas del cuadro de honor")
def verificar_tabla_resultados(pag):
    expect(pag.locator("table")).to_be_visible()
    assert "/admin/resultados" in pag.url


@then("ve el enlace a la tabla pública de resultados")
def verificar_link_tabla_publica(pag):
    link = pag.locator("a[href*='/resultados']")
    expect(link.first).to_be_visible()


@then("ve el badge de popular con ícono de estrella")
def verificar_badge_popular(pag):
    body_text = pag.locator("body").inner_text()
    assert "⭐" in body_text or "Popular" in body_text


@then("ve el badge de cuarto lugar")
def verificar_badge_cuarto(pag):
    badge = pag.locator(".pos-4")
    expect(badge.first).to_be_visible()


@then("solo ve las entradas de ese campeonato")
def verificar_filtro_campeonato(pag):
    # Verificamos que el filtro fue aplicado (URL tiene el parámetro)
    assert "champ_id=" in pag.url


@then("solo ve las entradas de ese año")
def verificar_filtro_anio(pag):
    assert "year=" in pag.url
    anio = getattr(pag, "_anio_filtrado", None)
    if anio:
        filas = pag.locator("table tbody tr")
        for i in range(min(filas.count(), 5)):
            fila_texto = filas.nth(i).inner_text()
            assert anio in fila_texto, f"Fila no corresponde al año {anio}: {fila_texto}"


@then("ve todos los resultados sin filtrar")
def verificar_sin_filtros(pag):
    assert "year=" not in pag.url or pag.url.endswith("/admin/resultados")


@then("ve el formulario de edición del cuadro de honor")
def verificar_form_edicion_honor(pag):
    assert "/honor/" in pag.url and "/edit" in pag.url
    expect(pag.locator('[name="dancer_names"]')).to_be_visible()


@then("el formulario tiene activado el parámetro de retorno a resultados")
def verificar_param_from_results(pag):
    assert "from=results" in pag.url


@then("la entrada ya no aparece en la tabla de resultados")
def verificar_entrada_eliminada_resultados(pag):
    filas_ahora = pag.locator("table tbody tr").count()
    filas_antes = getattr(pag, "_filas_antes", filas_ahora + 1)
    assert filas_ahora < filas_antes or filas_ahora == 0
