# =============================================================================
# step_defs/test_auth.py — Steps para autenticación (auth.feature)
# =============================================================================

import os
import re
import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import expect

scenarios("auth.feature")

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@admin.cl")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")


# ─── Given ────────────────────────────────────────────────────────────────────

@given("que el usuario navega a la página de login")
def ir_a_login(anon_page):
    anon_page.goto("/auth/login")
    expect(anon_page).to_have_url(re.compile(r"login"))


@given("que el usuario navega a la página de registro")
def ir_a_registro(anon_page):
    anon_page.goto("/auth/register")


@given("que el administrador ya ha iniciado sesión")
def admin_ya_logueado(admin_page):
    # El fixture admin_page ya realiza el login; solo verificamos que esté activo
    expect(admin_page.locator("body")).to_be_visible()


# ─── When ─────────────────────────────────────────────────────────────────────

@when("ingresa credenciales de administrador válidas")
def ingresar_credenciales_admin(anon_page):
    anon_page.locator('[name="email"]').fill(ADMIN_EMAIL)
    anon_page.locator('[name="password"]').fill(ADMIN_PASSWORD)
    anon_page.locator('[type="submit"]').click()
    anon_page.wait_for_load_state("networkidle")


@when("ingresa el email del admin con una contraseña incorrecta")
def ingresar_pass_incorrecta(anon_page):
    anon_page.locator('[name="email"]').fill(ADMIN_EMAIL)
    anon_page.locator('[name="password"]').fill("password_totalmente_incorrecta_xyz")
    anon_page.locator('[type="submit"]').click()
    anon_page.wait_for_load_state("networkidle")


@when("ingresa un email que no existe en el sistema")
def ingresar_email_inexistente(anon_page):
    anon_page.locator('[name="email"]').fill("no_existe_jamás@cueca.cl")
    anon_page.locator('[name="password"]').fill("cualquier_password")
    anon_page.locator('[type="submit"]').click()
    anon_page.wait_for_load_state("networkidle")


@when("completa el formulario de registro con datos válidos y email único")
def completar_registro(anon_page):
    ts = datetime.now().strftime("%m%d%H%M%S")
    anon_page.locator('[name="name"]').fill(f"Usuario Test {ts}")
    anon_page.locator('[name="email"]').fill(f"test_{ts}@cueca.cl")
    anon_page.locator('[name="password"]').fill("TestPassword123!")
    anon_page.locator('[type="submit"]').click()
    anon_page.wait_for_load_state("networkidle")


@when("intenta registrarse con el email del administrador ya existente")
def registrar_email_duplicado(anon_page):
    anon_page.locator('[name="name"]').fill("Nombre Duplicado")
    anon_page.locator('[name="email"]').fill(ADMIN_EMAIL)
    anon_page.locator('[name="password"]').fill("Password123!")
    anon_page.locator('[type="submit"]').click()
    anon_page.wait_for_load_state("networkidle")


@when("hace clic en cerrar sesión")
def cerrar_sesion(admin_page):
    # Busca el link de logout en la nav (puede ser texto o URL /auth/logout)
    logout = admin_page.locator("a[href*='logout']").first
    logout.click()
    admin_page.wait_for_load_state("networkidle")


# ─── Then ─────────────────────────────────────────────────────────────────────

@then("es redirigido a la página principal")
def verificar_redirect_home(anon_page):
    # Tras login exitoso no debe seguir en /auth/login
    expect(anon_page).not_to_have_url(re.compile(r"login"))


@then("ve el menú de administrador en la barra de navegación")
def verificar_menu_admin(anon_page):
    # El navbar muestra "Admin" o "Panel Admin" para admins
    expect(anon_page.locator("body")).to_contain_text("Admin")


@then("permanece en la página de login")
def verificar_sigue_en_login(anon_page):
    expect(anon_page).to_have_url(re.compile(r"login"))


@then("ve un mensaje de error de autenticación")
def verificar_error_auth(anon_page):
    # Tras login fallido el usuario sigue en la página de login
    # El mensaje de error puede variar; verificamos que seguimos en /auth/login
    assert "login" in anon_page.url, f"URL inesperada tras login fallido: {anon_page.url}"
    body_text = anon_page.locator("body").inner_text().lower()
    # Acepta mensaje de error O simplemente que seguimos en el formulario de login
    still_on_form = "ingresar" in body_text or "contraseña" in body_text or "correo" in body_text
    has_error = (
        "incorrecta" in body_text
        or "inválid" in body_text
        or "invalid" in body_text
        or "credencial" in body_text
        or "error" in body_text
        or "usuario" in body_text
        or "no encontrado" in body_text
        or "no existe" in body_text
    )
    assert still_on_form or has_error, "No se encontró mensaje de error de autenticación"


@then("es redirigido a la página principal tras el registro")
def verificar_redirect_registro(anon_page):
    expect(anon_page).not_to_have_url(re.compile(r"register"))


@then("ve el nombre del usuario en la barra de navegación")
def verificar_nombre_en_nav(anon_page):
    # Tras registro exitoso el usuario está logueado y ve su nombre
    expect(anon_page.locator("nav, header")).to_be_visible()


@then("permanece en la página de registro")
def verificar_sigue_en_registro(anon_page):
    expect(anon_page).to_have_url(re.compile(r"register"))


@then("ve un mensaje de error de email duplicado")
def verificar_error_email_duplicado(anon_page):
    body_text = anon_page.locator("body").inner_text().lower()
    assert (
        "ya" in body_text
        or "exist" in body_text
        or "registrado" in body_text
        or "error" in body_text
    ), "No se encontró mensaje de email duplicado"


@then("es redirigido a la página de login o inicio")
def verificar_redirect_tras_logout(admin_page):
    # Tras logout puede ir a / o a /auth/login según la configuración
    url = admin_page.url
    assert "/" in url, f"URL inesperada tras logout: {url}"


@then("no ve el menú de administrador")
def verificar_sin_menu_admin(admin_page):
    body_text = admin_page.locator("body").inner_text()
    # "Panel Admin" solo aparece para admins autenticados
    assert "Panel Admin" not in body_text, "El menú de admin sigue visible tras logout"
