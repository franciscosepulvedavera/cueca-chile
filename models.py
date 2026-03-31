# =============================================================================
# models.py — Modelos de base de datos (SQLAlchemy ORM)
#
# Tablas del sistema:
#   User            — cuentas con roles (user | moderator | admin)
#   Event           — eventos de cueca
#   Notification    — alertas in-app
#   Championship    — campeonatos nacionales
#   HonorEntry      — posiciones 0-4 por año, categoría y región
#                     position=0 → "Pareja más popular" (reconocimiento especial)
#                     position=1-4 → lugares competitivos
#   HonorEntryLink  — redes sociales de la pareja ganadora
#   ContentCreator  — directorio de creadores (url opcional)
#   CreatorLink     — redes sociales del creador
#   Store           — directorio de tiendas
#   StoreLink       — redes sociales de la tienda
#   StoreContact    — números de contacto de la tienda
# =============================================================================

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


# ─────────────────────────────────────────────────────────────────────────────
# Usuario
# ─────────────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    """
    Cuenta de usuario del sistema.
    Roles: user | moderator | admin
    """
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name          = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), default="user")
    banned        = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    events        = db.relationship("Event", backref="author", lazy=True)
    notifications = db.relationship("Notification", backref="recipient", lazy="dynamic")

    def set_password(self, pwd: str):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.password_hash, pwd)

    @property
    def unread_notifications(self):
        return self.notifications.filter_by(read=False).count()


# ─────────────────────────────────────────────────────────────────────────────
# Evento
# ─────────────────────────────────────────────────────────────────────────────
class Event(db.Model):
    """Evento de cueca (pending → approved/rejected → expired)."""
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    kind         = db.Column(db.String(30),  nullable=False, index=True)
    date         = db.Column(db.Date, nullable=False, index=True)
    end_date     = db.Column(db.Date, nullable=True)
    region       = db.Column(db.String(80),  nullable=False)
    comuna       = db.Column(db.String(120), nullable=False)
    place        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.String(200), nullable=True)
    bases_url    = db.Column(db.String(500), nullable=True)
    image_path   = db.Column(db.String(500), nullable=False)
    status       = db.Column(db.String(20), default="pending", index=True)
    expired      = db.Column(db.Boolean, default=False, index=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    user_id      = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ─────────────────────────────────────────────────────────────────────────────
# Notificación
# ─────────────────────────────────────────────────────────────────────────────
class Notification(db.Model):
    """Notificación in-app. link redirige al recurso relevante al hacer click."""
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    link       = db.Column(db.String(500), nullable=True)
    read       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Campeonato Nacional
# ─────────────────────────────────────────────────────────────────────────────
class Championship(db.Model):
    """
    Campeonato nacional de cueca.
    active=False lo oculta del sitio público.
    """
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location    = db.Column(db.String(200), nullable=True)
    image_path  = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    honor_entries = db.relationship(
        "HonorEntry", backref="championship",
        lazy="dynamic", cascade="all, delete-orphan",
    )
    links = db.relationship(
        "ChampionshipLink", backref="championship",
        lazy=True, cascade="all, delete-orphan",
    )

    def years(self):
        """Años únicos con entradas, de más reciente a más antiguo."""
        from sqlalchemy import distinct
        result = (
            db.session.query(distinct(HonorEntry.year))
            .filter_by(championship_id=self.id)
            .order_by(HonorEntry.year.desc()).all()
        )
        return [r[0] for r in result]


# ─────────────────────────────────────────────────────────────────────────────
# Link de Red Social — Campeonato
# ─────────────────────────────────────────────────────────────────────────────
class ChampionshipLink(db.Model):
    """Red social o URL de un campeonato. platform: instagram|tiktok|facebook|website"""
    id                = db.Column(db.Integer, primary_key=True)
    championship_id   = db.Column(db.Integer, db.ForeignKey("championship.id"), nullable=False)
    platform          = db.Column(db.String(30),  nullable=False)
    url               = db.Column(db.String(500), nullable=False)
    label             = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Entrada del Cuadro de Honor
# ─────────────────────────────────────────────────────────────────────────────
class HonorEntry(db.Model):
    """
    Resultado de un campeonato: posición obtenida por una pareja.

    Valores de position:
      0 → ⭐ Pareja más popular (reconocimiento especial, no competitivo)
      1 → 🥇 1° Lugar
      2 → 🥈 2° Lugar
      3 → 🥉 3° Lugar
      4 → 4° Lugar

    El campo position=0 NO se contabiliza en la Tabla de Resultados
    ya que esta solo cuenta lugares competitivos (1-4... para futuros
    campeonatos se puede ampliar fácilmente).

    comuna: campo nuevo opcional para campeonatos que distinguen por ciudad.
    links:  redes sociales de la pareja ganadora (HonorEntryLink).
    """
    id              = db.Column(db.Integer, primary_key=True)
    championship_id = db.Column(db.Integer, db.ForeignKey("championship.id"), nullable=False)
    year            = db.Column(db.Integer, nullable=False)
    category        = db.Column(db.String(100), nullable=False)
    position        = db.Column(db.Integer, nullable=False)      # 0, 1, 2, 3 o 4
    dancer_names    = db.Column(db.String(300), nullable=False)
    region          = db.Column(db.String(80),  nullable=False)
    comuna          = db.Column(db.String(120), nullable=True)   # NUEVO: ciudad/comuna (opcional)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Redes sociales de la pareja ganadora
    links = db.relationship(
        "HonorEntryLink", backref="entry",
        lazy=True, cascade="all, delete-orphan",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Link de Red Social — Pareja del Cuadro de Honor
# ─────────────────────────────────────────────────────────────────────────────
class HonorEntryLink(db.Model):
    """
    Red social o perfil público de una pareja del cuadro de honor.
    platform: 'instagram' | 'tiktok' | 'facebook' | 'youtube' | 'website'
    label: nombre del integrante u otra etiqueta (ej: "Instagram de Juan")
    """
    id       = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("honor_entry.id"), nullable=False)
    platform = db.Column(db.String(30),  nullable=False)
    url      = db.Column(db.String(500), nullable=False)
    label    = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Creador de Contenido
# ─────────────────────────────────────────────────────────────────────────────
class ContentCreator(db.Model):
    """
    Canal, perfil o cuenta dedicada a contenido de cueca.

    url: URL principal (OPCIONAL). Si no se especifica, se usan los links
         de redes sociales (CreatorLink).
    """
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path  = db.Column(db.String(500), nullable=True)
    url         = db.Column(db.String(500), nullable=True)   # CAMBIADO: ahora opcional
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    links = db.relationship(
        "CreatorLink", backref="creator",
        lazy=True, cascade="all, delete-orphan",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Link de Red Social — Creador de Contenido
# ─────────────────────────────────────────────────────────────────────────────
class CreatorLink(db.Model):
    """
    Red social o plataforma de un creador de contenido.
    platform: 'instagram' | 'tiktok' | 'facebook' | 'youtube' | 'twitch' | 'website'
    """
    id         = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("content_creator.id"), nullable=False)
    platform   = db.Column(db.String(30),  nullable=False)
    url        = db.Column(db.String(500), nullable=False)
    label      = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Tienda
# ─────────────────────────────────────────────────────────────────────────────
class Store(db.Model):
    """
    Tienda especializada en cueca.
    address: dirección física del local (NUEVO, opcional).
    website_url: URL del sitio web principal (opcional).
    links/contacts: redes sociales y teléfonos (tablas relacionadas).
    """
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path  = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    address     = db.Column(db.String(300), nullable=True)   # NUEVO: dirección física
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    links    = db.relationship("StoreLink",    backref="store", lazy=True,
                               cascade="all, delete-orphan")
    contacts = db.relationship("StoreContact", backref="store", lazy=True,
                               cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
# Link de Red Social — Tienda
# ─────────────────────────────────────────────────────────────────────────────
class StoreLink(db.Model):
    """Red social o URL de una tienda. platform: instagram|tiktok|facebook|website"""
    id       = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    platform = db.Column(db.String(30),  nullable=False)
    url      = db.Column(db.String(500), nullable=False)
    label    = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Contacto — Tienda
# ─────────────────────────────────────────────────────────────────────────────
class StoreContact(db.Model):
    """Número de contacto de una tienda. kind: phone|whatsapp"""
    id       = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    kind     = db.Column(db.String(20), nullable=False)
    value    = db.Column(db.String(50),  nullable=False)
    label    = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Músico / Agrupación
# ─────────────────────────────────────────────────────────────────────────────
class Musician(db.Model):
    """
    Músico, cantante o agrupación de cueca.
    Solo el nombre es obligatorio. Todos los demás campos son opcionales.
    links:    redes sociales (MusicianLink)
    contacts: medios de contacto — email, teléfono, whatsapp (MusicianContact)
    """
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_path  = db.Column(db.String(500), nullable=True)
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    links    = db.relationship("MusicianLink",    backref="musician", lazy=True,
                               cascade="all, delete-orphan")
    contacts = db.relationship("MusicianContact", backref="musician", lazy=True,
                               cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
# Link de Red Social — Músico
# ─────────────────────────────────────────────────────────────────────────────
class MusicianLink(db.Model):
    """Red social o plataforma de un músico."""
    id          = db.Column(db.Integer, primary_key=True)
    musician_id = db.Column(db.Integer, db.ForeignKey("musician.id"), nullable=False)
    platform    = db.Column(db.String(30),  nullable=False)
    url         = db.Column(db.String(500), nullable=False)
    label       = db.Column(db.String(100), nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
# Contacto — Músico
# ─────────────────────────────────────────────────────────────────────────────
class MusicianContact(db.Model):
    """
    Medio de contacto de un músico.
    kind: email | phone | whatsapp
    """
    id          = db.Column(db.Integer, primary_key=True)
    musician_id = db.Column(db.Integer, db.ForeignKey("musician.id"), nullable=False)
    kind        = db.Column(db.String(20), nullable=False)  # email|phone|whatsapp
    value       = db.Column(db.String(200), nullable=False)
    label       = db.Column(db.String(100), nullable=True)
