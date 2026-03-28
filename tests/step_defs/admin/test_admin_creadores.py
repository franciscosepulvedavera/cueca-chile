# =============================================================================
# step_defs/admin/test_admin_creadores.py — Steps para admin_creadores.feature
# =============================================================================

import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("admin/admin_creadores.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el administrador ha iniciado sesión en el panel", target_fixture="pag")
def admin_en_panel(admin_page):
    return admin_page


@given("que existe al menos un creador en el sistema")
def creador_existe(pag):
    pag.goto("/admin/creadores")
    pag.wait_for_load_state("networkidle")
    filas = pag.locator("table tbody tr")
    if filas.count() == 0 or "Sin creadores" in pag.locator("body").inner_text():
        pytest.skip("No hay creadores en el sistema")


@given("que existe un creador de prueba para eliminar")
def crear_creador_para_eliminar(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag.goto("/admin/creadores/new")
    pag.wait_for_load_state("networkidle")
    pag._creador_a_eliminar = f"ELIMINAR Creador {ts}"
    pag.locator('[name="name"]').fill(pag._creador_a_eliminar)
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la gestión de creadores")
def navegar_gestion_creadores(pag):
    pag.goto("/admin/creadores")
    pag.wait_for_load_state("networkidle")


@when("hace clic en nuevo creador")
def clic_nuevo_creador(pag):
    pag.locator("a[href*='/creadores/new'], a:has-text('Nuevo creador')").first.click()
    pag.wait_for_load_state("networkidle")


@when("completa el formulario de creador con nombre y URL principal únicos")
def completar_form_creador_con_url(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_creador = f"Creador Test {ts}"
    pag.locator('[name="name"]').fill(pag._nombre_creador)
    pag.locator('[name="description"]').fill("Descripción del creador de prueba")
    pag.locator('[name="url"]').fill(f"https://youtube.com/@test{ts}")


@when("completa el formulario de creador con nombre único sin URL")
def completar_form_creador_sin_url(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_creador = f"Creador SinURL {ts}"
    pag.locator('[name="name"]').fill(pag._nombre_creador)
    pag.locator('[name="description"]').fill("Creador sin URL principal")
    # Dejamos el campo URL vacío intencionalmente


@when("agrega una red social de instagram al creador")
def agregar_red_social_creador(pag):
    pag.locator("button:has-text('Agregar red social'), .add-row-btn").first.click()
    pag.wait_for_timeout(300)
    pag.locator('[name="link_platform[]"]').last.select_option("instagram")
    pag.locator('[name="link_url[]"]').last.fill("https://instagram.com/creador_test")


@when("envía el formulario de creador")
def enviar_form_creador(pag):
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en editar el primer creador")
def clic_editar_creador(pag):
    pag.locator("a[href*='/edit'], a:has-text('Editar')").first.click()
    pag.wait_for_load_state("networkidle")


@when("modifica el nombre del creador")
def modificar_nombre_creador(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_editado = f"Creador Editado {ts}"
    campo = pag.locator('[name="name"]')
    campo.clear()
    campo.fill(pag._nombre_editado)


@when("elimina el creador de prueba")
def eliminar_creador_prueba(pag):
    nombre = getattr(pag, "_creador_a_eliminar", None)
    if not nombre:
        pytest.skip("No hay creador de prueba para eliminar")
    fila = pag.locator(f"tr:has-text('{nombre[:20]}')")
    if fila.count() == 0:
        pytest.skip("No se encontró el creador de prueba en la tabla")
    pag.once("dialog", lambda d: d.accept())
    fila.locator("form button").first.click()
    pag.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página de administración de creadores")
def verificar_pag_admin_creadores(pag):
    assert "/admin/creadores" in pag.url


@then("ve el botón para agregar nuevo creador")
def verificar_boton_nuevo_creador(pag):
    expect(pag.locator("a:has-text('Nuevo creador'), a[href*='/new']").first).to_be_visible()


@then("ve un mensaje de éxito de creador guardado")
def verificar_flash_creador_guardado(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "guardado" in body_text.lower() or "creado" in body_text.lower()


@then("el nuevo creador aparece en la lista")
def verificar_creador_en_lista(pag):
    nombre = getattr(pag, "_nombre_creador", None)
    if nombre:
        expect(pag.locator("body")).to_contain_text(nombre[:20])


@then("el campo URL no tiene el marcador de obligatorio")
def verificar_url_opcional(pag):
    # El label del campo URL no debe tener la clase "required"
    label_url = pag.locator("label[for*='url']")
    if label_url.is_visible():
        label_html = label_url.inner_html()
        assert "required" not in label_html or "opcional" in pag.locator("body").inner_text().lower()


@then("ve un mensaje de éxito de creador actualizado")
def verificar_flash_creador_actualizado(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "actualizado" in body_text.lower() or "guardado" in body_text.lower()


@then("el creador eliminado ya no aparece en la lista")
def verificar_creador_eliminado(pag):
    nombre = getattr(pag, "_creador_a_eliminar", "ELIMINAR Creador")
    # Navegar de nuevo para descartar el flash message que también contiene el nombre
    pag.goto("/admin/creadores")
    pag.wait_for_load_state("networkidle")
    body_text = pag.locator("body").inner_text()
    assert nombre[:20] not in body_text
