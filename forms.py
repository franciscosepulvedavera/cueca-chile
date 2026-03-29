# =============================================================================
# forms.py — Formularios Flask-WTF con validación del lado servidor
# =============================================================================

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, TextAreaField, DateField,
    FileField, SubmitField, PasswordField, EmailField,
    IntegerField, BooleanField,
)
from wtforms.validators import DataRequired, URL, Length, Email, Optional, NumberRange

# ─────────────────────────────────────────────────────────────────────────────
# Constantes compartidas
# ─────────────────────────────────────────────────────────────────────────────

# Regiones de Chile — orden oficial Norte→Sur
REGIONES = [
    ("Arica y Parinacota", "Arica y Parinacota"),
    ("Tarapacá",           "Tarapacá"),
    ("Antofagasta",        "Antofagasta"),
    ("Atacama",            "Atacama"),
    ("Coquimbo",           "Coquimbo"),
    ("Valparaíso",         "Valparaíso"),
    ("Metropolitana",      "Metropolitana"),
    ("O'Higgins",          "O'Higgins"),
    ("Maule",              "Maule"),
    ("Ñuble",              "Ñuble"),
    ("Biobío",             "Biobío"),
    ("La Araucanía",       "La Araucanía"),
    ("Los Ríos",           "Los Ríos"),
    ("Los Lagos",          "Los Lagos"),
    ("Aysén",              "Aysén"),
    ("Magallanes",         "Magallanes"),
]

# Plataformas para tiendas
STORE_PLATFORMS = [
    ("instagram", "Instagram"),
    ("tiktok",    "TikTok"),
    ("facebook",  "Facebook"),
    ("website",   "Sitio Web"),
]

# Tipos de contacto para tiendas
STORE_CONTACT_KINDS = [
    ("phone",    "Teléfono"),
    ("whatsapp", "WhatsApp"),
]

# Plataformas para el cuadro de honor (redes de la pareja)
HONOR_PLATFORMS = [
    ("instagram", "Instagram"),
    ("tiktok",    "TikTok"),
    ("facebook",  "Facebook"),
    ("youtube",   "YouTube"),
    ("website",   "Sitio Web"),
]

# Plataformas para creadores de contenido
CREATOR_PLATFORMS = [
    ("instagram", "Instagram"),
    ("tiktok",    "TikTok"),
    ("facebook",  "Facebook"),
    ("youtube",   "YouTube"),
    ("twitch",    "Twitch"),
    ("website",   "Sitio Web"),
]

# Plataformas para músicos
MUSICIAN_PLATFORMS = [
    ("instagram",  "Instagram"),
    ("tiktok",     "TikTok"),
    ("facebook",   "Facebook"),
    ("youtube",    "YouTube"),
    ("spotify",    "Spotify"),
    ("soundcloud", "SoundCloud"),
    ("website",    "Sitio Web"),
]

# Tipos de contacto para músicos
MUSICIAN_CONTACT_KINDS = [
    ("email",    "Email"),
    ("phone",    "Teléfono"),
    ("whatsapp", "WhatsApp"),
]

# Posiciones del cuadro de honor:
#   0 = Pareja más popular (reconocimiento especial, no competitivo)
#   1-4 = lugares competitivos
# Se usa como constante para mantener la lista en un solo lugar.
HONOR_POSITIONS = [
    ("1", "🥇 1° Lugar"),
    ("2", "🥈 2° Lugar"),
    ("3", "🥉 3° Lugar"),
    ("4", "4° Lugar"),
    ("0", "⭐ Pareja más popular"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Autenticación
# ─────────────────────────────────────────────────────────────────────────────

class RegisterForm(FlaskForm):
    name     = StringField("Nombre",       validators=[DataRequired(), Length(min=2, max=120)])
    email    = EmailField("Email",         validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit   = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    email    = EmailField("Email",         validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit   = SubmitField("Ingresar")


# ─────────────────────────────────────────────────────────────────────────────
# Eventos
# ─────────────────────────────────────────────────────────────────────────────

class EventForm(FlaskForm):
    """El campo comuna se populan por JS según la región seleccionada."""
    title        = StringField("Título", validators=[DataRequired(), Length(max=120)])
    kind         = SelectField("Tipo", choices=[
        ("Nacionales","Nacionales"),("Regionales","Regionales"),
        ("Abiertos/Masivos","Abiertos/Masivos"),("Cuecazos","Cuecazos"),("Benéfico","Benéfico"),
    ], validators=[DataRequired()])
    date         = DateField("Fecha de inicio",              validators=[DataRequired()])
    end_date     = DateField("Fecha de término (opcional)",  validators=[Optional()])
    region       = SelectField("Región",  choices=REGIONES,  validators=[DataRequired()])
    comuna       = SelectField("Comuna",  choices=[],         validators=[DataRequired()])
    place        = StringField("Dirección / Lugar", validators=[DataRequired(), Length(max=200)])
    description  = TextAreaField("Descripción", validators=[DataRequired()])
    contact_info = StringField("Contacto", validators=[Optional(), Length(max=200)],
                               description="Teléfono, email, Instagram u otro contacto (opcional)")
    bases_url    = StringField("Enlace a bases (PDF)", validators=[Optional(), URL()])
    image        = FileField("Imagen del evento (JPG/PNG/WEBP)", validators=[DataRequired()])
    submit       = SubmitField("Enviar a revisión")


# ─────────────────────────────────────────────────────────────────────────────
# Panel admin
# ─────────────────────────────────────────────────────────────────────────────

class AdminUserActionForm(FlaskForm):
    """Solo CSRF token. Protege botones destructivos contra CSRF."""
    submit = SubmitField("OK")


class ChangeRoleForm(FlaskForm):
    role = SelectField("Rol", choices=[
        ("user","Usuario"),("moderator","Moderador"),("admin","Administrador"),
    ], validators=[DataRequired()])
    submit = SubmitField("Cambiar rol")


# ─────────────────────────────────────────────────────────────────────────────
# Campeonatos
# ─────────────────────────────────────────────────────────────────────────────

class ChampionshipForm(FlaskForm):
    name        = StringField("Nombre del campeonato", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Descripción",          validators=[Optional()])
    location    = StringField("Lugar habitual",         validators=[Optional(), Length(max=200)])
    website_url = StringField("Sitio web",              validators=[Optional(), URL()])
    image       = FileField("Imagen (JPG/PNG/WEBP)",    validators=[Optional()])
    active      = BooleanField("Activo (visible en el sitio)", default=True)
    submit      = SubmitField("Guardar campeonato")


class HonorEntryForm(FlaskForm):
    """
    Crear o editar una entrada del cuadro de honor.

    Posiciones disponibles:
      1-4 → lugares competitivos (contabilizados en la Tabla de Resultados)
      0   → Pareja más popular (reconocimiento especial, no competitivo)

    comarca: campo opcional para campeonatos que requieren especificar
             la ciudad o comuna de origen de la pareja.

    Los links de redes sociales de la pareja se manejan fuera de WTForms
    (campos dinámicos en el template, parseados directamente en el blueprint).
    """
    year         = IntegerField("Año", validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    category     = StringField("Categoría", validators=[DataRequired(), Length(max=100)],
                               description="Ej: Adulto, Juvenil, Infantil, Senior")
    position     = SelectField(
        "Distinción",
        choices=HONOR_POSITIONS,
        validators=[DataRequired()],
        coerce=int,
    )
    dancer_names = StringField("Pareja / Nombre(s)", validators=[DataRequired(), Length(max=300)],
                               description="Ej: Juan Pérez / María López")
    region       = SelectField("Región", choices=REGIONES, validators=[DataRequired()])
    comuna       = StringField(
        "Comuna / Ciudad",
        validators=[Optional(), Length(max=120)],
        description="Opcional: especifica la ciudad si el campeonato lo requiere",
    )
    submit       = SubmitField("Guardar")


# ─────────────────────────────────────────────────────────────────────────────
# Creadores de Contenido
# ─────────────────────────────────────────────────────────────────────────────

class ContentCreatorForm(FlaskForm):
    """
    url: OPCIONAL. Si el creador no tiene URL principal, se usan sus links
         de redes sociales para mostrar los botones de acceso.
    Los links de redes se manejan como campos dinámicos fuera de WTForms.
    """
    name        = StringField("Nombre",   validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripción breve", validators=[Optional()])
    url         = StringField(
        "URL principal (opcional)",
        validators=[Optional(), URL()],
        description="Canal principal, sitio web, etc. Si no tienes, deja vacío.",
    )
    image       = FileField("Foto / Logo (JPG/PNG/WEBP)", validators=[Optional()])
    active      = BooleanField("Visible en el sitio", default=True)
    submit      = SubmitField("Guardar")


# ─────────────────────────────────────────────────────────────────────────────
# Tiendas
# ─────────────────────────────────────────────────────────────────────────────

class StoreForm(FlaskForm):
    """
    Campos base de una tienda. Links y contactos se manejan dinámicamente.
    address: dirección física del local (opcional).
    """
    name        = StringField("Nombre de la tienda", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripción breve", validators=[Optional()])
    website_url = StringField("Sitio web (opcional)", validators=[Optional(), URL()])
    address     = StringField(
        "Dirección / Local físico",
        validators=[Optional(), Length(max=300)],
        description="Ej: Av. Providencia 123, Local 4, Santiago. Déjalo vacío si es solo online.",
    )
    image       = FileField("Logo / Imagen (JPG/PNG/WEBP)", validators=[Optional()])
    active      = BooleanField("Visible en el sitio", default=True)
    submit      = SubmitField("Guardar")


# ─────────────────────────────────────────────────────────────────────────────
# Músicos
# ─────────────────────────────────────────────────────────────────────────────

class MusicianForm(FlaskForm):
    """
    Solo el nombre es obligatorio.
    Links de redes sociales y contactos se manejan dinámicamente (fuera de WTForms).
    """
    name        = StringField("Nombre del músico o agrupación", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Descripción breve", validators=[Optional()])
    image       = FileField("Foto / Logo (JPG/PNG/WEBP)", validators=[Optional()])
    active      = BooleanField("Visible en el sitio", default=True)
    submit      = SubmitField("Guardar")
