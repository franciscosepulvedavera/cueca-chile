# =============================================================================
# tests/conftest.py — Fixtures globales y hooks de reporte para la suite
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
import base64
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


# ─── Opciones de Playwright ───────────────────────────────────────────────────

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


# =============================================================================
# REPORTE: captura de pasos, screenshots y métricas por escenario
# =============================================================================

# Almacenamiento en memoria durante la sesión
_step_logs  = {}   # {nodeid: [ {keyword, name, status, screenshot, error, url} ]}
_test_pages = {}   # {nodeid: page}  — referencia al objeto Page activo


def _find_page(args: dict):
    """Busca el objeto Page en un dict de fixtures/args."""
    for name in ("admin_page", "anon_page", "pagina", "pag", "page"):
        obj = args.get(name)
        if obj is not None:
            return obj
    return None


def _capture_screenshot(page) -> str | None:
    """Devuelve screenshot en base64 o None si falla."""
    try:
        return base64.b64encode(page.screenshot(full_page=True)).decode()
    except Exception:
        return None


def _current_url(page) -> str:
    """Devuelve la URL actual del navegador o cadena vacía."""
    try:
        return page.url
    except Exception:
        return ""


# ── Hook: inicio de escenario ─────────────────────────────────────────────────

@pytest.hookimpl
def pytest_bdd_before_scenario(request, feature, scenario):
    nodeid = request.node.nodeid
    _step_logs[nodeid] = []
    # Intenta cachear la página desde los fixtures ya inicializados
    page = _find_page(request.node.funcargs)
    if page:
        _test_pages[nodeid] = page


# ── Hook: paso completado con éxito ───────────────────────────────────────────

@pytest.hookimpl
def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    nodeid = request.node.nodeid
    page = _find_page(step_func_args) or _test_pages.get(nodeid)
    if page:
        _test_pages[nodeid] = page

    _step_logs.setdefault(nodeid, []).append({
        "keyword":    step.keyword,
        "name":       step.name,
        "status":     "passed",
        "screenshot": _capture_screenshot(page) if page else None,
        "url":        _current_url(page) if page else "",
        "error":      None,
    })


# ── Hook: paso fallido ────────────────────────────────────────────────────────

@pytest.hookimpl
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    nodeid = request.node.nodeid
    page = _find_page(step_func_args) or _test_pages.get(nodeid)
    if page:
        _test_pages[nodeid] = page

    _step_logs.setdefault(nodeid, []).append({
        "keyword":    step.keyword,
        "name":       step.name,
        "status":     "failed",
        "screenshot": _capture_screenshot(page) if page else None,
        "url":        _current_url(page) if page else "",
        "error":      str(exception),
    })


# ── Construcción del bloque HTML de pasos ─────────────────────────────────────

_KW_COLORS = {
    "Given": "#5B8DD9",
    "When":  "#5BAD6F",
    "Then":  "#D4AC0D",
    "And":   "#9B59B6",
    "But":   "#E74C3C",
}


def _build_steps_html(steps: list) -> str:
    """Genera el bloque HTML colapsable con pasos y screenshots."""
    if not steps:
        return ""

    parts = [
        '<div style="font-family:\'Courier New\', monospace; font-size:12px; '
        'margin-top:10px; border-top:1px solid #e0e0e0; padding-top:8px;">'
        '<strong style="font-size:13px; color:#333;">📋 Pasos del escenario</strong>'
    ]

    for step in steps:
        passed  = step["status"] == "passed"
        icon    = "✅" if passed else "❌"
        border  = "#4CAF50" if passed else "#F44336"
        kw_col  = _KW_COLORS.get(step["keyword"], "#666")
        bg      = "#f9fff9" if passed else "#fff5f5"

        parts.append(
            f'<details style="margin:4px 0; border-left:3px solid {border}; '
            f'background:{bg}; padding:4px 8px; border-radius:0 4px 4px 0;">'
            f'<summary style="cursor:pointer; list-style:none; padding:2px 0;">'
            f'{icon} '
            f'<span style="color:{kw_col}; font-weight:bold;">{step["keyword"]}</span> '
            f'{step["name"]}'
        )

        if step.get("url"):
            parts.append(
                f' <span style="color:#999; font-size:10px; margin-left:8px;">'
                f'🌐 {step["url"]}</span>'
            )

        parts.append('</summary>')

        if step.get("error"):
            err_safe = (
                step["error"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            parts.append(
                f'<pre style="background:#ffebee; color:#c62828; padding:8px; '
                f'margin:6px 0; border-radius:4px; font-size:11px; '
                f'overflow-x:auto; white-space:pre-wrap;">{err_safe}</pre>'
            )

        if step.get("screenshot"):
            parts.append(
                f'<div style="margin:6px 0;">'
                f'<img src="data:image/png;base64,{step["screenshot"]}" '
                f'style="max-width:100%; border:1px solid #ddd; border-radius:4px; '
                f'cursor:zoom-in; display:block;" '
                f'onclick="this.style.maxWidth=this.style.maxWidth===\'100%\'?\'none\':\'100%\'" />'
                f'</div>'
            )

        parts.append('</details>')

    parts.append('</div>')
    return "".join(parts)


# ── Hook: adjuntar HTML al reporte pytest-html ────────────────────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()

    if report.when != "call":
        return

    html_plugin = item.config.pluginmanager.getplugin("html")
    if not html_plugin:
        return

    nodeid = item.nodeid
    steps  = _step_logs.get(nodeid, [])

    extras = getattr(report, "extras", [])

    if steps:
        extras.append(html_plugin.extras.html(_build_steps_html(steps)))

    # Screenshot final (estado de la página al terminar el test)
    page = _test_pages.get(nodeid)
    if page and report.failed:
        sc = _capture_screenshot(page)
        if sc:
            extras.append(html_plugin.extras.image(sc, mime_type="image/png"))

    report.extras = extras


# ── Personalización del reporte HTML ──────────────────────────────────────────

def pytest_html_report_title(report):
    report.title = "🎶 Cueca Chile — Reporte de Pruebas"


def pytest_configure(config):
    config._metadata = {
        "Proyecto":  "🎶 Cueca Chile",
        "URL":       BASE_URL,
        "Navegador": BROWSER_NAME,
        "Headless":  str(HEADLESS),
        "Fecha":     datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Admin":     ADMIN_EMAIL,
    }
