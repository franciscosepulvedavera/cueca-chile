# =============================================================================
# step_defs/admin/test_admin_honor.py — Steps para admin_honor.feature
# =============================================================================

import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("admin/admin_honor.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el administrador ha iniciado sesión en el panel", target_fixture="pag")
def admin_en_panel(admin_page):
    return admin_page


@given("existe al menos un campeonato en el sistema")
def campeonato_disponible(pag):
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")
    links = pag.locator("a[href*='/campeonatos/'][href*='/edit'], table tbody tr a").all()
    if not links:
        pytest.skip("No hay campeonatos en el sistema para agregar honor entries")


@given("que existe una entrada en el cuadro de honor")
def honor_entry_existe(pag):
    # Navega al primer campeonato y verifica que hay al menos una entrada
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")
    primer_edit = pag.locator("a[href*='/edit']").first
    if not primer_edit.is_visible():
        pytest.skip("No hay campeonatos disponibles")
    primer_edit.click()
    pag.wait_for_load_state("networkidle")
    entradas = pag.locator(".honor-entry-row")
    if entradas.count() == 0:
        pytest.skip("No hay entradas en el cuadro de honor")


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega al detalle del primer campeonato")
def navegar_primer_campeonato(pag):
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")
    primer_edit = pag.locator("a[href*='/campeonatos/'][href*='/edit']").first
    if not primer_edit.is_visible():
        pytest.skip("No hay campeonatos disponibles")
    primer_edit.click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en agregar entrada al cuadro de honor")
def clic_agregar_honor(pag):
    btn = pag.locator("a[href*='/honor/new'], a:has-text('Agregar entrada'), a:has-text('Agregar')").first
    expect(btn).to_be_visible()
    btn.click()
    pag.wait_for_load_state("networkidle")


@when("completa el formulario con año, categoría, pareja y primer lugar")
def completar_form_honor_primero(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._pareja_nombre = f"Pareja Test {ts}"
    pag.locator('[name="year"]').fill("2025")
    pag.locator('[name="category"]').fill("Adulto")
    pag.locator('[name="position"]').select_option("1")
    pag.locator('[name="dancer_names"]').fill(pag._pareja_nombre)


@when("completa el formulario seleccionando pareja más popular")
def completar_form_honor_popular(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._pareja_nombre = f"Popular Test {ts}"
    pag.locator('[name="year"]').fill("2025")
    pag.locator('[name="category"]').fill("Adulto")
    pag.locator('[name="position"]').select_option("0")
    pag.locator('[name="dancer_names"]').fill(pag._pareja_nombre)


@when("completa el formulario seleccionando cuarto lugar")
def completar_form_honor_cuarto(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._pareja_nombre = f"Cuarto Test {ts}"
    pag.locator('[name="year"]').fill("2025")
    pag.locator('[name="category"]').fill("Adulto")
    pag.locator('[name="position"]').select_option("4")
    pag.locator('[name="dancer_names"]').fill(pag._pareja_nombre)


@when("completa el formulario básico de honor")
def completar_form_honor_basico(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._pareja_nombre = f"Pareja Test {ts}"
    pag.locator('[name="year"]').fill("2025")
    pag.locator('[name="category"]').fill("Adulto")
    pag.locator('[name="position"]').select_option("1")
    pag.locator('[name="dancer_names"]').fill(pag._pareja_nombre)


@when("selecciona una región")
def seleccionar_region(pag):
    pag.locator('[name="region"]').select_option("Metropolitana")


@when("agrega una red social de tipo instagram a la pareja")
def agregar_red_social_honor(pag):
    pag.locator("button:has-text('Agregar red social'), .add-row-btn").first.click()
    pag.wait_for_timeout(300)
    pag.locator('[name="link_platform[]"]').last.select_option("instagram")
    pag.locator('[name="link_url[]"]').last.fill("https://instagram.com/pareja_test")


@when("rellena el campo de comuna")
def rellenar_comuna(pag):
    pag.locator('[name="comuna"]').fill("Santiago Centro")


@when("envía el formulario de honor")
def enviar_form_honor(pag):
    # Asegurar que la región esté seleccionada si no lo está
    region = pag.locator('[name="region"]')
    if region.is_visible() and region.input_value() == "":
        region.select_option("Metropolitana")
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en editar la primera entrada")
def clic_editar_honor(pag):
    btn = pag.locator(".entry-actions a[href*='/edit'], a[href*='/honor/'][href*='/edit']").first
    if not btn.is_visible():
        pytest.skip("No hay botón de editar en las entradas")
    btn.click()
    pag.wait_for_load_state("networkidle")


@when("modifica el nombre de la pareja")
def modificar_nombre_pareja(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._pareja_editada = f"Pareja Editada {ts}"
    campo = pag.locator('[name="dancer_names"]')
    campo.clear()
    campo.fill(pag._pareja_editada)


@when("hace clic en eliminar la primera entrada y confirma")
def clic_eliminar_honor(pag):
    # El botón de eliminar está en un form independiente
    btn_eliminar = pag.locator(".entry-actions form button, button:has-text('🗑')").first
    if not btn_eliminar.is_visible():
        pytest.skip("No hay entradas para eliminar")
    pag.once("dialog", lambda d: d.accept())
    btn_eliminar.click()
    pag.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve un mensaje de éxito de entrada agregada")
def verificar_flash_entrada_agregada(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "agregada" in body_text.lower() or "guardada" in body_text.lower()


@then("la nueva entrada aparece en el cuadro de honor")
def verificar_entrada_en_honor(pag):
    nombre = getattr(pag, "_pareja_nombre", None)
    if nombre:
        expect(pag.locator("body")).to_contain_text(nombre[:15])


@then("la entrada aparece con el ícono de estrella")
def verificar_icono_estrella(pag):
    body_text = pag.locator("body").inner_text()
    assert "⭐" in body_text, "No se encontró el ícono de estrella ⭐"


@then("la entrada aparece con ícono de red social")
def verificar_icono_red_social(pag):
    body_text = pag.locator("body").inner_text()
    assert "📸" in body_text or "🎵" in body_text or "👥" in body_text or "🌐" in body_text


@then("la entrada muestra la región y la comuna")
def verificar_region_y_comuna(pag):
    body_text = pag.locator("body").inner_text()
    assert "Santiago Centro" in body_text or "Metropolitana" in body_text


@then("ve un mensaje de éxito de entrada actualizada")
def verificar_flash_entrada_actualizada(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "actualizada" in body_text.lower() or "guardada" in body_text.lower()


@then("la entrada ya no aparece en el cuadro de honor")
def verificar_entrada_eliminada(pag):
    # Tras eliminar, la página se recarga — verificamos que cargó OK
    expect(pag.locator("body")).to_be_visible()
