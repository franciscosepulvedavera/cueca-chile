# =============================================================================
# step_defs/admin/test_admin_tiendas.py — Steps para admin_tiendas.feature
# =============================================================================

import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("admin/admin_tiendas.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el administrador ha iniciado sesión en el panel", target_fixture="pag")
def admin_en_panel(admin_page):
    return admin_page


@given("que existe al menos una tienda en el sistema")
def tienda_existe(pag):
    pag.goto("/admin/tiendas")
    pag.wait_for_load_state("networkidle")
    if "Sin tiendas" in pag.locator("body").inner_text():
        pytest.skip("No hay tiendas en el sistema")


@given("que existe una tienda de prueba para eliminar")
def crear_tienda_para_eliminar(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag.goto("/admin/tiendas/new")
    pag.wait_for_load_state("networkidle")
    pag._tienda_a_eliminar = f"ELIMINAR Tienda {ts}"
    pag.locator('[name="name"]').fill(pag._tienda_a_eliminar)
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la gestión de tiendas")
def navegar_gestion_tiendas(pag):
    pag.goto("/admin/tiendas")
    pag.wait_for_load_state("networkidle")


@when("hace clic en nueva tienda")
def clic_nueva_tienda(pag):
    pag.locator("a[href*='/tiendas/new'], a:has-text('Nueva tienda'), a:has-text('Nueva')").first.click()
    pag.wait_for_load_state("networkidle")


@when("completa el formulario de tienda con nombre único y dirección física")
def completar_form_tienda_con_dir(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_tienda = f"Tienda Test {ts}"
    pag.locator('[name="name"]').fill(pag._nombre_tienda)
    pag.locator('[name="description"]').fill("Tienda de cueca de prueba")
    pag.locator('[name="address"]').fill(f"Av. Providencia 123, Local {ts[-4:]}, Santiago")


@when("completa el formulario de tienda con nombre único")
def completar_form_tienda_basico(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_tienda = f"Tienda Test {ts}"
    pag.locator('[name="name"]').fill(pag._nombre_tienda)
    pag.locator('[name="description"]').fill("Tienda de cueca de prueba")


@when("agrega una red social de instagram a la tienda")
def agregar_red_social_tienda(pag):
    pag.locator("button:has-text('Agregar red social'), .add-row-btn").first.click()
    pag.wait_for_timeout(300)
    pag.locator('[name="link_platform[]"]').last.select_option("instagram")
    pag.locator('[name="link_url[]"]').last.fill("https://instagram.com/tienda_test")


@when("agrega un número de contacto WhatsApp")
def agregar_contacto_whatsapp(pag):
    pag.locator("button:has-text('Agregar número'), button:has-text('contacto')").first.click()
    pag.wait_for_timeout(300)
    pag.locator('[name="contact_kind[]"]').last.select_option("whatsapp")
    pag.locator('[name="contact_value[]"]').last.fill("+56 9 1234 5678")


@when("envía el formulario de tienda")
def enviar_form_tienda(pag):
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en editar la primera tienda")
def clic_editar_tienda(pag):
    pag.locator("a[href*='/edit'], a:has-text('Editar')").first.click()
    pag.wait_for_load_state("networkidle")


@when("modifica el nombre de la tienda")
def modificar_nombre_tienda(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_editado = f"Tienda Editada {ts}"
    campo = pag.locator('[name="name"]')
    campo.clear()
    campo.fill(pag._nombre_editado)


@when("elimina la tienda de prueba")
def eliminar_tienda_prueba(pag):
    nombre = getattr(pag, "_tienda_a_eliminar", None)
    if not nombre:
        pytest.skip("No hay tienda de prueba para eliminar")
    fila = pag.locator(f"tr:has-text('{nombre[:20]}')")
    if fila.count() == 0:
        pytest.skip("No se encontró la tienda de prueba")
    pag.once("dialog", lambda d: d.accept())
    fila.locator("form button").first.click()
    pag.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página de administración de tiendas")
def verificar_pag_admin_tiendas(pag):
    assert "/admin/tiendas" in pag.url


@then("ve el botón para agregar nueva tienda")
def verificar_boton_nueva_tienda(pag):
    expect(pag.locator("a:has-text('Nueva'), a[href*='/new']").first).to_be_visible()


@then("ve un mensaje de éxito de tienda guardada")
def verificar_flash_tienda_guardada(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "guardada" in body_text.lower() or "creada" in body_text.lower()


@then("la nueva tienda aparece en la lista")
def verificar_tienda_en_lista(pag):
    nombre = getattr(pag, "_nombre_tienda", None)
    if nombre:
        expect(pag.locator("body")).to_contain_text(nombre[:20])


@then("ve un mensaje de éxito de tienda actualizada")
def verificar_flash_tienda_actualizada(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "actualizada" in body_text.lower() or "guardada" in body_text.lower()


@then("la tienda eliminada ya no aparece en la lista")
def verificar_tienda_eliminada(pag):
    nombre = getattr(pag, "_tienda_a_eliminar", "ELIMINAR Tienda")
    # Navegar de nuevo para descartar el flash message que también contiene el nombre
    pag.goto("/admin/tiendas")
    pag.wait_for_load_state("networkidle")
    assert nombre[:20] not in pag.locator("body").inner_text()
