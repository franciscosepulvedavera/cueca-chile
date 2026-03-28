# =============================================================================
# step_defs/test_eventos.py — Steps para eventos (eventos.feature)
# =============================================================================

import os
import re
import pytest
from datetime import datetime, date, timedelta
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

scenarios("eventos.feature")

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@admin.cl")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que un visitante anónimo accede al sitio", target_fixture="pagina")
def visitante_anonimo(anon_page):
    return anon_page


@given("que el administrador ya ha iniciado sesión", target_fixture="pagina")
def admin_logueado(admin_page):
    return admin_page


# ─── When ─────────────────────────────────────────────────────────────────────

@when("navega a la sección de eventos")
def navegar_eventos(pagina):
    pagina.goto("/")
    pagina.wait_for_load_state("networkidle")


@when("intenta acceder directamente al formulario de nuevo evento")
def acceder_form_evento_sin_login(pagina):
    pagina.goto("/events/new")
    pagina.wait_for_load_state("networkidle")


@when("navega al formulario de nuevo evento")
def navegar_form_evento(pagina):
    pagina.goto("/events/new")
    pagina.wait_for_load_state("networkidle")


@when("crea un nuevo evento con todos los datos válidos")
def crear_evento_admin(pagina):
    pagina.goto("/events/new")
    pagina.wait_for_load_state("networkidle")

    ts    = datetime.now().strftime("%m%d%H%M%S")
    fecha = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")

    pagina.locator('[name="title"]').fill(f"Evento Test {ts}")
    pagina.locator('[name="kind"]').select_option("Nacionales")
    pagina.locator('[name="date"]').fill(fecha)
    pagina.locator('[name="region"]').select_option("Metropolitana")

    # Esperar que el select de comuna se cargue por JS
    pagina.wait_for_timeout(800)
    comunas = pagina.locator('[name="comuna"]')
    if comunas.is_visible():
        comunas.select_option(index=1)

    pagina.locator('[name="place"]').fill(f"Teatro Municipal Test {ts}")
    pagina.locator('[name="description"]').fill("Descripción del evento de prueba automatizado")

    # La imagen es requerida — sube un archivo de prueba pequeño
    imagen_path = _crear_imagen_temporal()
    pagina.locator('[name="image"]').set_input_files(imagen_path)

    pagina.locator('[type="submit"]').click()
    pagina.wait_for_load_state("networkidle")


@when("puede hacer clic en el primer evento disponible")
@then("puede hacer clic en el primer evento disponible")
def clic_primer_evento(pagina):
    primer_evento = pagina.locator("a[href*='/events/']").first
    if not primer_evento.is_visible():
        pytest.skip("No hay eventos aprobados en el sistema")
    primer_evento.click()
    pagina.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("ve la lista de eventos aprobados")
def verificar_lista_eventos(pagina):
    expect(pagina.locator("body")).to_be_visible()


@then("ve el título de la sección de eventos")
def verificar_titulo_eventos(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    assert "evento" in body_text or "cueca" in body_text


@then("es redirigido a la página de login")
def verificar_redirect_login(pagina):
    expect(pagina).to_have_url(re.compile(r"login"))


@then("no puede crear el evento sin autenticarse")
def verificar_no_puede_crear(pagina):
    # Si está en login, no llegó al formulario
    assert "login" in pagina.url


@then("ve el formulario con los campos requeridos")
def verificar_form_evento(pagina):
    expect(pagina.locator('[name="title"]')).to_be_visible()
    expect(pagina.locator('[name="description"]')).to_be_visible()


@then("ve los campos título, tipo, fecha, región y descripción")
def verificar_campos_evento(pagina):
    for campo in ["title", "kind", "date", "region", "description"]:
        expect(pagina.locator(f'[name="{campo}"]')).to_be_visible()


@then("el evento es creado exitosamente")
def verificar_evento_creado(pagina):
    # Admin publica directo, no va a moderación
    url = pagina.url
    assert "new" not in url or "eventos" in url


@then("ve un mensaje de confirmación de publicación")
def verificar_flash_evento(pagina):
    body_text = pagina.locator("body").inner_text().lower()
    assert (
        "publicado" in body_text
        or "creado" in body_text
        or "enviado" in body_text
        or "exitoso" in body_text
        or "✅" in body_text
    ), "No se encontró mensaje de confirmación"


@then("ve la página de detalle con la información del evento")
def verificar_detalle_evento(pagina):
    expect(pagina.locator("h1, h2")).to_be_visible()


# ─── Helper ───────────────────────────────────────────────────────────────────

def _crear_imagen_temporal() -> str:
    """Crea un PNG mínimo válido en /tmp para subirlo como imagen de prueba."""
    import struct, zlib, tempfile
    # PNG 1x1 pixel rojo mínimo
    def png_chunk(tag, data):
        chunk = tag + data
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr   = png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw    = b"\x00\xFF\x00\x00"
    idat   = png_chunk(b"IDAT", zlib.compress(raw))
    iend   = png_chunk(b"IEND", b"")
    png_data = header + ihdr + idat + iend

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(png_data)
    tmp.close()
    return tmp.name
