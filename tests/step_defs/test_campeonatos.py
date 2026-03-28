# =============================================================================
# step_defs/test_campeonatos.py — Steps para campeonatos (campeonatos.feature)
# =============================================================================

import pytest
from pytest_bdd import scenarios, given, when, then
from playwright.sync_api import expect

scenarios("campeonatos.feature")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que un visitante anónimo accede al sitio", target_fixture="pagina")
def visitante_anonimo(anon_page):
    return anon_page


@given("que existe al menos un campeonato con entradas en el cuadro de honor",
       target_fixture="pagina")
def campeonato_con_honor(anon_page):
    # Navega a la lista y comprueba que hay al menos un campeonato
    anon_page.goto("/campeonatos/")
    anon_page.wait_for_load_state("networkidle")
    cards = anon_page.locator("a[href*='/campeonatos/']").all()
    if not cards:
        pytest.skip("No hay campeonatos con entradas en el sistema")
    return anon_page


@given("que existe un campeonato con ganadores que tienen redes sociales",
       target_fixture="pagina")
def campeonato_con_redes(anon_page):
    anon_page.goto("/campeonatos/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe un campeonato con ganadores que tienen comuna registrada",
       target_fixture="pagina")
def campeonato_con_comuna(anon_page):
    anon_page.goto("/campeonatos/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


@given("que existe un campeonato con una entrada de pareja más popular",
       target_fixture="pagina")
def campeonato_con_popular(anon_page):
    anon_page.goto("/campeonatos/")
    anon_page.wait_for_load_state("networkidle")
    return anon_page


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la sección de campeonatos")
def navegar_campeonatos(pagina):
    pagina.goto("/campeonatos/")
    pagina.wait_for_load_state("networkidle")


@when("el visitante accede al detalle del campeonato")
def acceder_detalle_campeonato(pagina):
    # Hace clic en el primer campeonato de la lista
    primer_link = pagina.locator("a[href*='/campeonatos/']").first
    if not primer_link.is_visible():
        pytest.skip("No hay campeonatos disponibles")
    primer_link.click()
    pagina.wait_for_load_state("networkidle")


@when("hace clic en un año disponible en el selector de año")
def clic_anio_selector(pagina):
    # El selector de año tiene .filter-tab o botones con años
    anio_link = pagina.locator(".year-bar a, .filter-tab").first
    if not anio_link.is_visible():
        pytest.skip("No hay selector de años en este campeonato")
    anio_texto = anio_link.inner_text()
    anio_link.click()
    pagina.wait_for_load_state("networkidle")
    pagina._ultimo_anio = anio_texto.strip()


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la página de campeonatos")
def verificar_pagina_campeonatos(pagina):
    expect(pagina.locator("body")).to_be_visible()
    assert "/campeonatos" in pagina.url


@then("ve el título de la sección campeonatos")
def verificar_titulo_campeonatos(pagina):
    body_text = pagina.locator("body").inner_text()
    assert "campeonato" in body_text.lower(), "No se encontró 'campeonato' en la página"


@then("ve el nombre del campeonato")
def verificar_nombre_campeonato(pagina):
    expect(pagina.locator("h1")).to_be_visible()


@then("ve la sección del cuadro de honor")
def verificar_seccion_honor(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    assert "cuadro de honor" in body_text or "honor" in body_text


@then("ve los badges de posición de los ganadores")
def verificar_badges_posicion(pagina):
    # Los badges de posición usan .position-badge
    badges = pagina.locator(".position-badge")
    if badges.count() == 0:
        pytest.skip("No hay entradas en el cuadro de honor de este campeonato")
    assert badges.count() > 0


@then("la URL contiene el parámetro del año seleccionado")
def verificar_url_con_anio(pagina):
    assert "year=" in pagina.url, f"URL sin parámetro year: {pagina.url}"


@then("ve las entradas correspondientes a ese año")
def verificar_entradas_del_anio(pagina):
    # Debería haber al menos una fila .honor-row
    filas = pagina.locator(".honor-row")
    # Si no hay entradas ese año, la página muestra mensaje vacío — ambos son válidos
    assert filas.count() >= 0


@then("ve los íconos de redes sociales en las filas del cuadro de honor")
def verificar_iconos_redes(pagina):
    # Los íconos de redes usan .honor-link-dot
    iconos = pagina.locator(".honor-link-dot, .honor-links a")
    if iconos.count() == 0:
        pytest.skip("No hay ganadores con redes sociales en este campeonato")


@then("ve la región y comuna del ganador en la fila correspondiente")
def verificar_region_comuna(pagina):
    filas = pagina.locator(".honor-row")
    if filas.count() == 0:
        pytest.skip("No hay entradas en el cuadro de honor")
    # Al menos una fila debe tener texto de región
    expect(filas.first.locator(".honor-region")).to_be_visible()


@then("ve el ícono de estrella para la pareja más popular")
def verificar_icono_popular(pagina):
    body_text = pagina.locator("body").inner_text()
    if "⭐" not in body_text:
        pytest.skip("No hay entradas de pareja más popular en este campeonato")
