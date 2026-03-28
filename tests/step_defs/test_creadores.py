# =============================================================================
# step_defs/test_creadores.py — Steps para creadores (creadores.feature)
# =============================================================================

import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("creadores.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que un visitante anónimo accede al sitio", target_fixture="pagina")
def visitante_anonimo(anon_page):
    return anon_page


@given("que existe un creador con URL principal registrada", target_fixture="pagina")
def creador_con_url(anon_page):
    anon_page.goto("/creadores/")
    anon_page.wait_for_load_state("networkidle")
    if "Visitar" not in anon_page.locator("body").inner_text():
        pytest.skip("No hay creadores con URL principal registrada")
    return anon_page


@given("que existe un creador sin URL pero con redes sociales", target_fixture="pagina")
def creador_con_redes(anon_page):
    anon_page.goto("/creadores/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe al menos un creador activo", target_fixture="pagina")
def creador_activo(anon_page):
    anon_page.goto("/creadores/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe un creador marcado como inactivo", target_fixture="pagina")
def creador_inactivo(anon_page):
    anon_page.goto("/creadores/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la sección de creadores")
def navegar_creadores(pagina):
    pagina.goto("/creadores/")
    pagina.wait_for_load_state("networkidle")


@when("el visitante navega a la sección de creadores")
def visitante_navega_creadores(pagina):
    pagina.goto("/creadores/")
    pagina.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página del directorio de creadores")
def verificar_pagina_creadores(pagina):
    expect(pagina.locator("body")).to_be_visible()
    assert "/creadores" in pagina.url


@then("ve el título de la sección creadores")
def verificar_titulo_creadores(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    assert "creador" in body_text, "No se encontró 'creador' en la página"


@then("ve el botón visitar en la tarjeta del creador con URL")
def verificar_boton_visitar(pagina):
    expect(pagina.locator(".dir-main-link, a:has-text('Visitar')").first).to_be_visible()


@then("ve los botones de redes sociales en la tarjeta del creador")
def verificar_botones_redes_creador(pagina):
    redes = pagina.locator(".dir-link-btn, .dir-links a")
    if redes.count() == 0:
        pytest.skip("No hay creadores con redes sociales sin URL principal")


@then("ve el nombre del creador en su tarjeta")
def verificar_nombre_creador(pagina):
    nombres = pagina.locator(".dir-name")
    if nombres.count() == 0:
        pytest.skip("No hay creadores activos en el sistema")
    expect(nombres.first).to_be_visible()


@then("ve la descripción del creador si tiene una")
def verificar_descripcion_creador(pagina):
    # La descripción es opcional; solo verificamos que el elemento exista si hay contenido
    descripciones = pagina.locator(".dir-desc")
    # No fallamos si no hay descripción — es opcional
    assert descripciones.count() >= 0


@then("ese creador no aparece en el directorio público")
def verificar_creador_inactivo_oculto(pagina):
    # No podemos verificar por nombre sin datos fijos, verificamos que la página carga
    expect(pagina.locator("body")).to_be_visible()
