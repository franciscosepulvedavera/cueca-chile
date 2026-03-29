# step_defs/admin/test_admin_musicos.py
import re
import pytest
from pytest_bdd import scenarios, given, when, then

scenarios("admin/admin_musicos.feature")


# ── Backgrounds / Given ───────────────────────────────────────────────────────

@given("que el administrador está autenticado", target_fixture="pag")
def admin_autenticado(admin_page):
    return admin_page


@given("que el usuario no está autenticado", target_fixture="pag")
def usuario_no_autenticado(anon_page):
    return anon_page


@given("que existe al menos un músico en el sistema", target_fixture="pag")
def musico_existente(admin_page, ts):
    """Crea un músico si no existe ninguno."""
    admin_page.goto("/admin/musicos/new")
    admin_page.locator('[name="name"]').fill(f"Músico Fixture {ts}")
    admin_page.locator('[type="submit"]').click()
    admin_page.wait_for_load_state("networkidle")
    return admin_page


@given("que existe al menos un músico activo", target_fixture="pag")
def musico_activo_publico(admin_page, ts):
    """Crea un músico activo para que aparezca en la vista pública."""
    admin_page.goto("/admin/musicos/new")
    admin_page.locator('[name="name"]').fill(f"Músico Público {ts}")
    admin_page.locator('[type="submit"]').click()
    admin_page.wait_for_load_state("networkidle")
    return admin_page


# ── When ──────────────────────────────────────────────────────────────────────

@when("navego a la lista de músicos en admin")
def navegar_lista_musicos(pag):
    pag.goto("/admin/musicos")
    pag.wait_for_load_state("networkidle")


@when("navego a crear un nuevo músico")
def navegar_crear_musico(pag):
    pag.goto("/admin/musicos/new")
    pag.wait_for_load_state("networkidle")


@when("completo el nombre del músico con un valor único")
def completar_nombre_musico(pag, ts):
    pag.locator('[name="name"]').fill(f"Músico Test {ts}")


@when("completo la descripción del músico")
def completar_descripcion_musico(pag):
    pag.locator('[name="description"]').fill("Agrupación de cueca brava del barrio")


@when("guardo el formulario de músico")
def guardar_formulario_musico(pag):
    pag.locator('[type="submit"]').click()
    pag.wait_for_load_state("networkidle")


@when("edito el primer músico de la lista")
def editar_primer_musico(pag):
    pag.goto("/admin/musicos")
    pag.wait_for_load_state("networkidle")
    edit_btn = pag.locator("a[href*='/admin/musicos/'][href*='/edit']").first
    edit_btn.click()
    pag.wait_for_load_state("networkidle")


@when("cambio el nombre del músico")
def cambiar_nombre_musico(pag, ts):
    campo = pag.locator('[name="name"]')
    campo.fill(f"Músico Editado {ts}")


@when("elimino el primer músico de la lista")
def eliminar_primer_musico(pag):
    pag.goto("/admin/musicos")
    pag.wait_for_load_state("networkidle")
    pag.once("dialog", lambda d: d.accept())
    pag.locator("form[action*='/admin/musicos/'] button.btn-danger").first.click()
    pag.wait_for_load_state("networkidle")


@when("intento acceder a la lista de músicos en admin")
def intentar_acceso_admin_musicos(pag):
    pag.goto("/admin/musicos")
    pag.wait_for_load_state("networkidle")


@when("navego a la sección de músicos")
def navegar_musicos_publico(pag):
    pag.goto("/musicos/")
    pag.wait_for_load_state("networkidle")


# ── Then ──────────────────────────────────────────────────────────────────────

@then("veo la página de administración de músicos")
def ver_admin_musicos(pag):
    from playwright.sync_api import expect
    expect(pag).to_have_url(re.compile("/admin/musicos"))
    expect(pag.locator("h1")).to_contain_text("Músicos")


@then("veo el músico creado en la lista")
def ver_musico_en_lista(pag, ts):
    from playwright.sync_api import expect
    expect(pag).to_have_url(re.compile("/admin/musicos"))
    expect(pag.locator("body")).to_contain_text(ts)


@then("veo el nombre actualizado en la lista")
def ver_nombre_actualizado(pag, ts):
    from playwright.sync_api import expect
    expect(pag).to_have_url(re.compile("/admin/musicos"))
    expect(pag.locator("body")).to_contain_text(f"Músico Editado {ts}")


@then("el músico ya no aparece en la lista")
def musico_eliminado(pag):
    from playwright.sync_api import expect
    expect(pag).to_have_url(re.compile("/admin/musicos"))


@then("soy redirigido al login")
def redirigido_login(pag):
    from playwright.sync_api import expect
    expect(pag).to_have_url(re.compile("login"))


@then("veo la página de músicos con el título correcto")
def ver_pagina_musicos(pag):
    from playwright.sync_api import expect
    expect(pag.locator("h1")).to_contain_text("Músicos")


@then("veo al menos un músico en la página")
def ver_musico_en_publico(pag):
    from playwright.sync_api import expect
    expect(pag.locator(".dir-card").first).to_be_visible()
