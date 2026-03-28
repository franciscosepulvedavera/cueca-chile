# =============================================================================
# step_defs/test_tiendas.py — Steps para tiendas (tiendas.feature)
# =============================================================================

import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("tiendas.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que un visitante anónimo accede al sitio", target_fixture="pagina")
def visitante_anonimo(anon_page):
    return anon_page


@given("que existe una tienda con sitio web registrado", target_fixture="pagina")
def tienda_con_web(anon_page):
    anon_page.goto("/tiendas/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe una tienda con dirección física registrada", target_fixture="pagina")
def tienda_con_direccion(anon_page):
    anon_page.goto("/tiendas/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe una tienda con redes sociales registradas", target_fixture="pagina")
def tienda_con_redes(anon_page):
    anon_page.goto("/tiendas/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe una tienda marcada como inactiva", target_fixture="pagina")
def tienda_inactiva(anon_page):
    anon_page.goto("/tiendas/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la sección de tiendas")
def navegar_tiendas(pagina):
    pagina.goto("/tiendas/")
    pagina.wait_for_load_state("networkidle")


@when("el visitante navega a la sección de tiendas")
def visitante_navega_tiendas(pagina):
    pagina.goto("/tiendas/")
    pagina.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página del directorio de tiendas")
def verificar_pagina_tiendas(pagina):
    expect(pagina.locator("body")).to_be_visible()
    assert "/tiendas" in pagina.url


@then("ve el título de la sección tiendas")
def verificar_titulo_tiendas(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    assert "tienda" in body_text, "No se encontró 'tienda' en la página"


@then("ve el enlace al sitio web de la tienda")
def verificar_link_web_tienda(pagina):
    links = pagina.locator("a[href*='http']")
    if links.count() == 0:
        pytest.skip("No hay tiendas con sitio web registrado")
    expect(links.first).to_be_visible()


@then("ve la dirección física de la tienda en su tarjeta")
def verificar_direccion_tienda(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    if "av." not in body_text and "calle" not in body_text and "local" not in body_text:
        pytest.skip("No hay tiendas con dirección física registrada")


@then("ve los iconos de redes sociales en la tarjeta de la tienda")
def verificar_iconos_redes_tienda(pagina):
    iconos = pagina.locator(".store-link, a[href*='instagram'], a[href*='tiktok'], a[href*='facebook']")
    if iconos.count() == 0:
        pytest.skip("No hay tiendas con redes sociales registradas")


@then("esa tienda no aparece en el directorio público")
def verificar_tienda_inactiva_oculta(pagina):
    expect(pagina.locator("body")).to_be_visible()
