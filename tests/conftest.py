# =============================================================================
# tests/conftest.py — Fixtures globales para la suite de tests
#
# Uso:
#   cd tests/
#   pytest                          # corre todo
#   pytest -m auth                  # solo tests de autenticación
#   pytest -m admin                 # solo tests de admin
#   pytest -k "campeonatos"         # filtro por nombre
#   pytest --headed                 # con ventana visible (override de HEADLESS)
#
# Variables de entorno (.env.test):
#   BASE_URL        URL del servidor (default: http://127.0.0.1:5000)
#   ADMIN_EMAIL     Email del administrador
#   ADMIN_PASSWORD  Contraseña del administrador
#   HEADLESS        true/false (default: true)
#   BROWSER         chromium/firefox/webkit (default: chromium)
# =============================================================================

import os
import pytest
from datetime import datetime
from dotenv import load_dotenv

# Carga .env.test si existe, sin pisar variables ya definidas
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.test"), override=False)

# ─── Configuración desde entorno ──────────────────────────────────────────────
BASE_URL       = os.getenv("BASE_URL",        "http://127.0.0.1:5000")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",     "admin@admin.cl")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD",  "changeme")
HEADLESS       = os.getenv("HEADLESS",        "true").lower() == "true"
BROWSER_NAME   = os.getenv("BROWSER",         "chromium")


# ─── Opciones de Playwright (se inyectan en pytest-playwright) ────────────────

def pytest_addoption(parser):
    """Permite pasar --headed desde la CLI para ver el navegador."""
    pass  # pytest-playwright ya provee --headed / --browser


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configura headless según la variable de entorno."""
    return {**browser_type_launch_args, "headless": HEADLESS}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Inyecta base_url en todos los contextos → permite page.goto('/ruta')."""
    return {**browser_context_args, "base_url": BASE_URL}


# ─── Fixture de timestamp único ───────────────────────────────────────────────

@pytest.fixture(scope="session")
def ts():
    """
    Timestamp de sesión para generar nombres únicos de test.
    Evita colisiones entre ejecuciones: "Test Camp 0328-1430".
    """
    return datetime.now().strftime("%m%d-%H%M")


# ─── Helper de login ──────────────────────────────────────────────────────────

def do_login(page, email: str, password: str):
    """Flujo completo de login. Reutilizado por los fixtures de página."""
    page.goto("/auth/login")
    page.locator('[name="email"]').fill(email)
    page.locator('[name="password"]').fill(password)
    page.locator('[type="submit"]').click()
    page.wait_for_load_state("networkidle")


# ─── Páginas pre-autenticadas ─────────────────────────────────────────────────

@pytest.fixture
def admin_page(browser):
    """
    Página de Playwright con sesión de ADMINISTRADOR ya iniciada.
    Usar en tests de admin en lugar del fixture 'page' estándar.
    """
    ctx = browser.new_context(base_url=BASE_URL)
    pg  = ctx.new_page()
    do_login(pg, ADMIN_EMAIL, ADMIN_PASSWORD)
    yield pg
    ctx.close()


@pytest.fixture
def anon_page(browser):
    """Página sin sesión iniciada (usuario anónimo)."""
    ctx = browser.new_context(base_url=BASE_URL)
    pg  = ctx.new_page()
    pg.goto("/")
    yield pg
    ctx.close()


# ─── Datos de test helper ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def admin_credentials():
    """Credenciales del admin como dict."""
    return {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
