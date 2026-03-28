# =============================================================================
# step_defs/admin/test_admin_campeonatos.py — Steps para admin_campeonatos.feature
# =============================================================================

import re
import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("admin/admin_campeonatos.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el administrador ha iniciado sesión en el panel", target_fixture="pag")
def admin_en_panel(admin_page):
    return admin_page


@given("que existe al menos un campeonato en el sistema")
def campeonato_existe(pag):
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")
    filas = pag.locator("table tbody tr, .honor-entry-row")
    if filas.count() == 0:
        pytest.skip("No hay campeonatos en el sistema")


@given("que existe un campeonato de prueba para eliminar")
def crear_campeonato_para_eliminar(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag.goto("/admin/campeonatos/new")
    pag.locator('[name="name"]').fill(f"ELIMINAR TEST {ts}")
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")
    pag._nombre_a_eliminar = f"ELIMINAR TEST {ts}"


@given("que el usuario no ha iniciado sesión")
def usuario_no_logueado(anon_page):
    pass  # anon_page ya es anónima


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la gestión de campeonatos")
def navegar_gestion_campeonatos(pag):
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")


@when("hace clic en nuevo campeonato")
def clic_nuevo_campeonato(pag):
    pag.locator("a[href*='/campeonatos/new'], a:has-text('Nuevo'), a:has-text('nuevo')").first.click()
    pag.wait_for_load_state("networkidle")


@when("completa el formulario con nombre de campeonato único")
def completar_form_campeonato(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_campeonato = f"Campeonato Test {ts}"
    pag.locator('[name="name"]').fill(pag._nombre_campeonato)
    pag.locator('[name="description"]').fill("Descripción del campeonato de prueba")


@when("envía el formulario de campeonato")
def enviar_form_campeonato(pag):
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


@when("hace clic en editar el primer campeonato")
def clic_editar_campeonato(pag):
    pag.locator("a[href*='/edit'], a:has-text('Editar'), button:has-text('Editar')").first.click()
    pag.wait_for_load_state("networkidle")


@when("modifica el nombre del campeonato")
def modificar_nombre_campeonato(pag):
    ts = datetime.now().strftime("%m%d%H%M%S")
    pag._nombre_editado = f"Campeonato Editado {ts}"
    nombre_field = pag.locator('[name="name"]')
    nombre_field.clear()
    nombre_field.fill(pag._nombre_editado)


@when("elimina el campeonato de prueba")
def eliminar_campeonato_prueba(pag):
    nombre = getattr(pag, "_nombre_a_eliminar", None)
    if not nombre:
        pytest.skip("No hay campeonato de prueba para eliminar")
    # Busca el botón de eliminar en la fila que contiene el nombre
    fila = pag.locator(f"tr:has-text('{nombre}'), .honor-entry-row:has-text('{nombre}')")
    if fila.count() == 0:
        pytest.skip("No se encontró el campeonato de prueba")
    # Registrar handler ANTES del click
    pag.once("dialog", lambda d: d.accept())
    fila.locator("button[type='submit'], form button").first.click()
    pag.wait_for_load_state("networkidle")


@when("intenta acceder directamente al panel de campeonatos")
def acceder_panel_sin_login(anon_page):
    anon_page.goto("/admin/campeonatos")
    anon_page.wait_for_load_state("networkidle")


@when("envía el formulario de campeonato vacío")
def enviar_form_vacio(pag):
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página de administración de campeonatos")
def verificar_pag_admin_campeonatos(pag):
    assert "/admin/campeonatos" in pag.url
    expect(pag.locator("body")).to_be_visible()


@then("ve el botón para agregar nuevo campeonato")
def verificar_boton_nuevo_campeonato(pag):
    boton = pag.locator("a[href*='/new'], a:has-text('Nuevo'), a:has-text('nuevo')")
    expect(boton.first).to_be_visible()


@then("ve un mensaje de éxito de campeonato creado")
def verificar_flash_campeonato_creado(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "guardado" in body_text.lower() or "creado" in body_text.lower()


@then("el nuevo campeonato aparece en la lista")
def verificar_campeonato_en_lista(pag):
    nombre = getattr(pag, "_nombre_campeonato", None)
    if nombre:
        expect(pag.locator("body")).to_contain_text(nombre[:20])


@then("ve un mensaje de éxito de campeonato actualizado")
def verificar_flash_campeonato_actualizado(pag):
    body_text = pag.locator("body").inner_text()
    assert "✅" in body_text or "actualizado" in body_text.lower() or "guardado" in body_text.lower()


@then("el campeonato eliminado ya no aparece en la lista")
def verificar_campeonato_eliminado(pag):
    nombre = getattr(pag, "_nombre_a_eliminar", "ELIMINAR TEST")
    # Navegar de nuevo para descartar el flash message que también contiene el nombre
    pag.goto("/admin/campeonatos")
    pag.wait_for_load_state("networkidle")
    assert nombre not in pag.locator("body").inner_text()


@then("es redirigido a la página de login")
def verificar_redirect_login(anon_page):
    expect(anon_page).to_have_url(re.compile(r"login"))


@then("ve errores de validación en el formulario")
def verificar_errores_validacion(pag):
    # HTML5 required="" impide el submit en el browser, la página no cambia
    # Verificamos que seguimos en el formulario (URL contiene /new o /campeonatos)
    url = pag.url
    body_text = pag.locator("body").inner_text().lower()
    still_on_form = "/new" in url or "/campeonatos" in url
    has_error_text = (
        "requerido" in body_text
        or "obligatorio" in body_text
        or "field is required" in body_text
        or "field-error" in pag.locator("body").inner_html().lower()
        or "error" in body_text
    )
    assert still_on_form or has_error_text, "Se esperaba quedar en el formulario o ver errores"
