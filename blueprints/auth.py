# =============================================================================
# blueprints/auth.py — Autenticación de usuarios
#
# Rutas:
#   GET/POST /auth/register  — Crear nueva cuenta
#   GET/POST /auth/login     — Iniciar sesión
#   GET      /auth/logout    — Cerrar sesión
#
# También define el `user_loader` de Flask-Login, que reconstruye el objeto
# `current_user` en cada request a partir del ID almacenado en la sesión.
# =============================================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User
from forms import RegisterForm, LoginForm

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


# ── Flask-Login: reconstruir current_user desde el ID en sesión ───────────────
@login_manager.user_loader
def load_user(user_id):
    """Callback que Flask-Login llama en cada request para cargar el usuario activo."""
    return User.query.get(int(user_id))


# ── Registro ──────────────────────────────────────────────────────────────────
@bp_auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Muestra y procesa el formulario de registro.
    Si el usuario ya está autenticado, lo redirige al inicio.
    Verifica que el email no esté ya en uso antes de crear la cuenta.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        # Verificar si el email ya existe (búsqueda case-insensitive)
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("El email ya está registrado.", "error")
        else:
            user = User(name=form.name.data.strip(), email=form.email.data.lower())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Cuenta creada. Ahora puedes ingresar.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


# ── Login ─────────────────────────────────────────────────────────────────────
@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Muestra y procesa el formulario de inicio de sesión.
    Verifica credenciales y estado de la cuenta (baneada o no).
    Soporta parámetro `?next=` para redirigir al destino original tras el login.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.check_password(form.password.data):
            # Bloquear acceso si la cuenta está baneada
            if user.banned:
                flash("Tu cuenta está baneada. Contacta a soporte.", "error")
                return redirect(url_for("auth.login"))

            # Iniciar sesión con remember=True (cookie de 14 días, ver config.py)
            login_user(user, remember=True)
            flash("Bienvenido/a", "success")

            # Redirigir al destino original o al inicio
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)

        flash("Credenciales inválidas.", "error")

    return render_template("auth/login.html", form=form)


# ── Logout ────────────────────────────────────────────────────────────────────
@bp_auth.route("/logout")
@login_required
def logout():
    """Cierra la sesión del usuario actual y redirige al inicio."""
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("index"))
