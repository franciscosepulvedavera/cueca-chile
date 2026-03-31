# =============================================================================
# blueprints/admin.py — Panel de Administración
#
# Secciones:
#   /admin/usuarios    — CRUD usuarios
#   /admin/campeonatos — CRUD campeonatos + cuadro de honor (con edición)
#   /admin/creadores   — CRUD creadores (url opcional + links dinámicos)
#   /admin/tiendas     — CRUD tiendas (dirección + links + contactos)
#   /admin/resultados  — Vista global de HonorEntry con edición/eliminación
# =============================================================================

import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, abort, current_app
)
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from models import (
    User, Championship, ChampionshipLink, HonorEntry, HonorEntryLink,
    ContentCreator, CreatorLink,
    Store, StoreLink, StoreContact,
    Musician, MusicianLink, MusicianContact,
)
from forms import (
    AdminUserActionForm, ChangeRoleForm,
    ChampionshipForm, HonorEntryForm,
    ContentCreatorForm, StoreForm,
    MusicianForm,
    CHAMPIONSHIP_PLATFORMS,
    STORE_PLATFORMS, STORE_CONTACT_KINDS,
    HONOR_PLATFORMS, CREATOR_PLATFORMS,
    MUSICIAN_PLATFORMS, MUSICIAN_CONTACT_KINDS,
)

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")
PER_PAGE = 20


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de acceso y utilidades
# ─────────────────────────────────────────────────────────────────────────────

def _require_admin():
    """Aborta con 403 si el usuario actual no es admin."""
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)


def _save_image_simple(file_storage) -> str | None:
    """
    Guarda una imagen sin redimensionar. Retorna la ruta relativa o None.
    Genera nombre único con timestamp para evitar colisiones de archivos.
    """
    if not file_storage or file_storage.filename == "":
        return None
    from werkzeug.utils import secure_filename
    from datetime import datetime
    filename  = secure_filename(file_storage.filename)
    base, ext = os.path.splitext(filename)
    filename  = f"{base}_{int(datetime.utcnow().timestamp())}{ext}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, filename))
    return f"uploads/{filename}"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de formularios dinámicos — Links genéricos
# ─────────────────────────────────────────────────────────────────────────────

def _parse_dynamic_links(prefix: str) -> list[dict]:
    """
    Parsea campos de links dinámicos del formulario actual.
    Espera: {prefix}_platform[], {prefix}_url[], {prefix}_label[]
    Solo guarda filas donde platform Y url tienen valor.
    """
    platforms = request.form.getlist(f"{prefix}_platform[]")
    urls      = request.form.getlist(f"{prefix}_url[]")
    labels    = request.form.getlist(f"{prefix}_label[]")
    result    = []
    for i, (plat, url) in enumerate(zip(platforms, urls)):
        plat  = plat.strip()
        url   = url.strip()
        label = labels[i].strip() if i < len(labels) else ""
        if plat and url:
            result.append({"platform": plat, "url": url, "label": label or None})
    return result


def _parse_store_contacts() -> list[dict]:
    """Parsea contactos dinámicos (phone/whatsapp) del formulario actual."""
    kinds  = request.form.getlist("contact_kind[]")
    values = request.form.getlist("contact_value[]")
    labels = request.form.getlist("contact_label[]")
    result = []
    for i, (kind, value) in enumerate(zip(kinds, values)):
        kind  = kind.strip()
        value = value.strip()
        label = labels[i].strip() if i < len(labels) else ""
        if kind and value:
            result.append({"kind": kind, "value": value, "label": label or None})
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de sincronización de relaciones
# ─────────────────────────────────────────────────────────────────────────────

def _sync_store_relations(store: Store, links: list[dict], contacts: list[dict]) -> None:
    """Reemplaza los links y contactos de una tienda con los nuevos datos."""
    StoreLink.query.filter_by(store_id=store.id).delete()
    StoreContact.query.filter_by(store_id=store.id).delete()
    for d in links:
        db.session.add(StoreLink(store_id=store.id, **d))
    for d in contacts:
        db.session.add(StoreContact(store_id=store.id, **d))


def _sync_creator_links(creator: ContentCreator, links: list[dict]) -> None:
    """Reemplaza los links de un creador con los nuevos datos."""
    CreatorLink.query.filter_by(creator_id=creator.id).delete()
    for d in links:
        db.session.add(CreatorLink(creator_id=creator.id, **d))


def _sync_championship_links(champ: Championship, links: list[dict]) -> None:
    """Reemplaza los links de un campeonato con los nuevos datos."""
    ChampionshipLink.query.filter_by(championship_id=champ.id).delete()
    for d in links:
        db.session.add(ChampionshipLink(championship_id=champ.id, **d))


def _sync_honor_links(entry: HonorEntry, links: list[dict]) -> None:
    """Reemplaza los links de una entrada de honor con los nuevos datos."""
    HonorEntryLink.query.filter_by(entry_id=entry.id).delete()
    for d in links:
        db.session.add(HonorEntryLink(entry_id=entry.id, **d))


# ══════════════════════════════════════════════════════════════════
#  USUARIOS
# ══════════════════════════════════════════════════════════════════

@bp_admin.route("/usuarios", methods=["GET"])
@login_required
def users():
    _require_admin()
    q           = (request.args.get("q") or "").strip()
    role_filter = request.args.get("role", "")
    page        = request.args.get("page", 1, type=int)
    query       = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like)))
    if role_filter:
        query = query.filter_by(role=role_filter)
    pagination  = query.order_by(User.created_at.desc()).paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("admin/users.html",
        users=pagination.items, pagination=pagination,
        q=q, role_filter=role_filter,
        form=AdminUserActionForm(), role_form=ChangeRoleForm())


@bp_admin.post("/usuarios/<int:user_id>/ban")
@login_required
def ban_user(user_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes banear tu propia cuenta.", "error"); return redirect(url_for("admin.users"))
    user.banned = True; db.session.commit()
    flash(f"Usuario {user.email} bloqueado.", "warning")
    return redirect(url_for("admin.users"))


@bp_admin.post("/usuarios/<int:user_id>/unban")
@login_required
def unban_user(user_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    user.banned = False; db.session.commit()
    flash(f"Usuario {user.email} desbloqueado.", "success")
    return redirect(url_for("admin.users"))


@bp_admin.post("/usuarios/<int:user_id>/role")
@login_required
def change_role(user_id):
    _require_admin()
    form = ChangeRoleForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes cambiar tu propio rol.", "error"); return redirect(url_for("admin.users"))
    new_role = form.role.data
    if new_role not in ("user", "moderator", "admin"): abort(400)
    user.role = new_role; db.session.commit()
    flash(f"Rol de {user.email} actualizado a «{new_role}».", "success")
    return redirect(url_for("admin.users"))


@bp_admin.post("/usuarios/<int:user_id>/delete")
@login_required
def delete_user(user_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.users"))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error"); return redirect(url_for("admin.users"))
    db.session.delete(user); db.session.commit()
    flash(f"Usuario {user.email} eliminado.", "info")
    return redirect(url_for("admin.users"))


# ══════════════════════════════════════════════════════════════════
#  CAMPEONATOS
# ══════════════════════════════════════════════════════════════════

@bp_admin.route("/campeonatos")
@login_required
def championships():
    """Lista todos los campeonatos con conteo de entradas de honor."""
    _require_admin()
    items = Championship.query.order_by(Championship.name.asc()).all()
    return render_template("admin/championships.html",
                           championships=items, form=AdminUserActionForm())


@bp_admin.route("/campeonatos/new", methods=["GET", "POST"])
@login_required
def championship_new():
    """Crear un nuevo campeonato. Redirige al listado con flash de confirmación."""
    _require_admin()
    form = ChampionshipForm()
    if form.validate_on_submit():
        try:
            img = _save_image_simple(form.image.data)
            c = Championship(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                location=form.location.data.strip()    if form.location.data    else None,
                website_url=form.website_url.data.strip() if form.website_url.data else None,
                image_path=img,
                active=form.active.data,
            )
            db.session.add(c)
            db.session.flush()
            _sync_championship_links(c, _parse_dynamic_links("champ"))
            db.session.commit()
            flash(f"✅ Campeonato «{c.name}» creado correctamente.", "success")
            return redirect(url_for("admin.championships"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar el campeonato. Error: {e}", "error")

    return render_template("admin/championship_form.html", form=form,
                           title="Nuevo campeonato", champ=None,
                           championship_platforms=CHAMPIONSHIP_PLATFORMS)


@bp_admin.route("/campeonatos/<int:champ_id>/edit", methods=["GET", "POST"])
@login_required
def championship_edit(champ_id):
    """
    Editar un campeonato existente.

    BUG CORREGIDO: el formulario del campeonato y los formularios de
    las entradas del cuadro de honor son completamente independientes
    en el HTML (no anidados). Los formularios anidados son inválidos en
    HTML y causaban que el botón Guardar no tuviese efecto visible.
    """
    _require_admin()
    c    = Championship.query.get_or_404(champ_id)
    form = ChampionshipForm(obj=c)

    if form.validate_on_submit():
        try:
            c.name        = form.name.data.strip()
            c.description = form.description.data.strip() if form.description.data else None
            c.location    = form.location.data.strip()    if form.location.data    else None
            c.website_url = form.website_url.data.strip() if form.website_url.data else None
            c.active      = form.active.data
            if form.image.data and form.image.data.filename:
                c.image_path = _save_image_simple(form.image.data)
            _sync_championship_links(c, _parse_dynamic_links("champ"))
            db.session.commit()
            flash(f"✅ Campeonato «{c.name}» actualizado correctamente.", "success")
            return redirect(url_for("admin.championships"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar el campeonato. Error: {e}", "error")

    return render_template("admin/championship_form.html", form=form,
                           title=f"Editar — {c.name}", champ=c,
                           championship_platforms=CHAMPIONSHIP_PLATFORMS)


@bp_admin.post("/campeonatos/<int:champ_id>/delete")
@login_required
def championship_delete(champ_id):
    """Elimina campeonato y todas sus entradas de honor (cascade)."""
    _require_admin()
    c = Championship.query.get_or_404(champ_id)
    name = c.name
    db.session.delete(c)
    db.session.commit()
    flash(f"Campeonato «{name}» eliminado.", "info")
    return redirect(url_for("admin.championships"))


# ── Cuadro de Honor ────────────────────────────────────────────────────────────

@bp_admin.route("/campeonatos/<int:champ_id>/honor/new", methods=["GET", "POST"])
@login_required
def honor_new(champ_id):
    """
    Agregar una nueva entrada al cuadro de honor.
    Incluye posiciones 0-4 (0 = Pareja más popular) y campo comuna opcional.
    También procesa los links dinámicos de redes sociales de la pareja.
    """
    _require_admin()
    champ = Championship.query.get_or_404(champ_id)
    form  = HonorEntryForm()

    if form.validate_on_submit():
        try:
            entry = HonorEntry(
                championship_id=champ.id,
                year=form.year.data,
                category=form.category.data.strip(),
                position=form.position.data,
                dancer_names=form.dancer_names.data.strip(),
                region=form.region.data,
                comuna=form.comuna.data.strip() if form.comuna.data else None,
            )
            db.session.add(entry)
            db.session.flush()  # obtener entry.id para los links

            # Guardar links de redes sociales de la pareja
            links = _parse_dynamic_links("link")
            _sync_honor_links(entry, links)

            db.session.commit()
            flash("✅ Entrada agregada al cuadro de honor.", "success")
            return redirect(url_for("admin.championship_edit", champ_id=champ.id))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar la entrada. Error: {e}", "error")

    return render_template("admin/honor_form.html", form=form, champ=champ,
                           title="+ Cuadro de Honor", is_edit=False,
                           platforms=HONOR_PLATFORMS)


@bp_admin.route("/campeonatos/<int:champ_id>/honor/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def honor_edit(champ_id, entry_id):
    """
    Editar una entrada existente del cuadro de honor.
    Pre-popula el formulario con los datos actuales (incluyendo links).
    """
    _require_admin()
    champ = Championship.query.get_or_404(champ_id)
    entry = HonorEntry.query.get_or_404(entry_id)

    if entry.championship_id != champ.id:
        abort(404)

    form = HonorEntryForm(obj=entry)

    if form.validate_on_submit():
        try:
            entry.year         = form.year.data
            entry.category     = form.category.data.strip()
            entry.position     = form.position.data
            entry.dancer_names = form.dancer_names.data.strip()
            entry.region       = form.region.data
            entry.comuna       = form.comuna.data.strip() if form.comuna.data else None

            links = _parse_dynamic_links("link")
            _sync_honor_links(entry, links)

            db.session.commit()
            flash("✅ Entrada actualizada correctamente.", "success")
            if request.args.get("from") == "results":
                return redirect(url_for("admin.admin_results"))
            return redirect(url_for("admin.championship_edit", champ_id=champ.id))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo actualizar la entrada. Error: {e}", "error")

    return render_template("admin/honor_form.html", form=form, champ=champ,
                           title=f"Editar entrada — {champ.name}",
                           is_edit=True, entry=entry,
                           platforms=HONOR_PLATFORMS)


@bp_admin.post("/campeonatos/<int:champ_id>/honor/<int:entry_id>/delete")
@login_required
def honor_delete(champ_id, entry_id):
    """Elimina una entrada del cuadro de honor."""
    _require_admin()
    entry = HonorEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entrada eliminada.", "info")
    if request.args.get("from") == "results":
        return redirect(url_for("admin.admin_results"))
    return redirect(url_for("admin.championship_edit", champ_id=champ_id))


# ══════════════════════════════════════════════════════════════════
#  RESULTADOS (ADMIN) — Vista global de todas las HonorEntry
# ══════════════════════════════════════════════════════════════════

@bp_admin.route("/resultados")
@login_required
def admin_results():
    """
    Vista de administración de todos los resultados.
    Filtros: campeonato, año. Permite editar y eliminar entradas.
    """
    _require_admin()
    champ_id_filter = request.args.get("champ_id", type=int)
    year_filter     = request.args.get("year",     type=int)
    page            = request.args.get("page",     1, type=int)

    query = HonorEntry.query
    if champ_id_filter: query = query.filter_by(championship_id=champ_id_filter)
    if year_filter:     query = query.filter_by(year=year_filter)

    query = query.join(Championship).order_by(
        Championship.name.asc(), HonorEntry.year.desc(),
        HonorEntry.category.asc(), HonorEntry.position.asc(),
    )
    pagination    = query.paginate(page=page, per_page=30, error_out=False)
    championships = Championship.query.order_by(Championship.name.asc()).all()
    years         = [y[0] for y in db.session.query(HonorEntry.year).distinct()
                     .order_by(HonorEntry.year.desc()).all()]

    return render_template("admin/results.html",
        entries=pagination.items, pagination=pagination,
        championships=championships, years=years,
        champ_id_filter=champ_id_filter, year_filter=year_filter,
        form=AdminUserActionForm())


# ══════════════════════════════════════════════════════════════════
#  CREADORES DE CONTENIDO
# ══════════════════════════════════════════════════════════════════

@bp_admin.route("/creadores")
@login_required
def creators():
    _require_admin()
    items = ContentCreator.query.order_by(ContentCreator.name.asc()).all()
    return render_template("admin/creators.html", creators=items, form=AdminUserActionForm())


@bp_admin.route("/creadores/new", methods=["GET", "POST"])
@login_required
def creator_new():
    """Crear creador. URL es opcional; los links de redes son dinámicos."""
    _require_admin()
    form = ContentCreatorForm()
    if form.validate_on_submit():
        try:
            img = _save_image_simple(form.image.data)
            c = ContentCreator(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                url=form.url.data.strip() if form.url.data else None,
                image_path=img,
                active=form.active.data,
            )
            db.session.add(c)
            db.session.flush()

            links = _parse_dynamic_links("link")
            _sync_creator_links(c, links)

            db.session.commit()
            flash(f"✅ Creador «{c.name}» agregado.", "success")
            return redirect(url_for("admin.creators"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar el creador. Error: {e}", "error")

    return render_template("admin/creator_form.html", form=form,
                           title="Nuevo creador",
                           platforms=CREATOR_PLATFORMS)


@bp_admin.route("/creadores/<int:creator_id>/edit", methods=["GET", "POST"])
@login_required
def creator_edit(creator_id):
    """Editar creador con URL opcional y links dinámicos."""
    _require_admin()
    c    = ContentCreator.query.get_or_404(creator_id)
    form = ContentCreatorForm(obj=c)
    if form.validate_on_submit():
        try:
            c.name        = form.name.data.strip()
            c.description = form.description.data.strip() if form.description.data else None
            c.url         = form.url.data.strip() if form.url.data else None
            c.active      = form.active.data
            if form.image.data and form.image.data.filename:
                c.image_path = _save_image_simple(form.image.data)

            links = _parse_dynamic_links("link")
            _sync_creator_links(c, links)

            db.session.commit()
            flash(f"✅ Creador «{c.name}» actualizado.", "success")
            return redirect(url_for("admin.creators"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo actualizar el creador. Error: {e}", "error")

    return render_template("admin/creator_form.html", form=form,
                           title=f"Editar — {c.name}", creator=c,
                           platforms=CREATOR_PLATFORMS)


@bp_admin.post("/creadores/<int:creator_id>/delete")
@login_required
def creator_delete(creator_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.creators"))
    c = ContentCreator.query.get_or_404(creator_id)
    db.session.delete(c); db.session.commit()
    flash(f"Creador «{c.name}» eliminado.", "info")
    return redirect(url_for("admin.creators"))


# ══════════════════════════════════════════════════════════════════
#  TIENDAS
# ══════════════════════════════════════════════════════════════════

@bp_admin.route("/tiendas")
@login_required
def stores():
    _require_admin()
    items = Store.query.order_by(Store.name.asc()).all()
    return render_template("admin/stores.html", stores=items, form=AdminUserActionForm())


@bp_admin.route("/tiendas/new", methods=["GET", "POST"])
@login_required
def store_new():
    """Crear tienda con dirección, links y contactos dinámicos."""
    _require_admin()
    form = StoreForm()
    if form.validate_on_submit():
        try:
            img = _save_image_simple(form.image.data)
            s = Store(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                website_url=form.website_url.data.strip()  if form.website_url.data  else None,
                address=form.address.data.strip()          if form.address.data       else None,
                image_path=img,
                active=form.active.data,
            )
            db.session.add(s)
            db.session.flush()

            links    = _parse_dynamic_links("link")
            contacts = _parse_store_contacts()
            _sync_store_relations(s, links, contacts)

            db.session.commit()
            flash(f"✅ Tienda «{s.name}» agregada.", "success")
            return redirect(url_for("admin.stores"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar la tienda. Error: {e}", "error")

    return render_template("admin/store_form.html", form=form,
                           title="Nueva tienda",
                           platforms=STORE_PLATFORMS, contact_kinds=STORE_CONTACT_KINDS)


@bp_admin.route("/tiendas/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
def store_edit(store_id):
    """Editar tienda con dirección, links y contactos dinámicos."""
    _require_admin()
    s    = Store.query.get_or_404(store_id)
    form = StoreForm(obj=s)
    if form.validate_on_submit():
        try:
            s.name        = form.name.data.strip()
            s.description = form.description.data.strip() if form.description.data else None
            s.website_url = form.website_url.data.strip()  if form.website_url.data  else None
            s.address     = form.address.data.strip()      if form.address.data       else None
            s.active      = form.active.data
            if form.image.data and form.image.data.filename:
                s.image_path = _save_image_simple(form.image.data)

            links    = _parse_dynamic_links("link")
            contacts = _parse_store_contacts()
            _sync_store_relations(s, links, contacts)

            db.session.commit()
            flash(f"✅ Tienda «{s.name}» actualizada.", "success")
            return redirect(url_for("admin.stores"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo actualizar la tienda. Error: {e}", "error")

    return render_template("admin/store_form.html", form=form,
                           title=f"Editar — {s.name}", store=s,
                           platforms=STORE_PLATFORMS, contact_kinds=STORE_CONTACT_KINDS)


@bp_admin.post("/tiendas/<int:store_id>/delete")
@login_required
def store_delete(store_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.stores"))
    s = Store.query.get_or_404(store_id)
    db.session.delete(s); db.session.commit()
    flash(f"Tienda «{s.name}» eliminada.", "info")
    return redirect(url_for("admin.stores"))


# ══════════════════════════════════════════════════════════════════
#  MÚSICOS
# ══════════════════════════════════════════════════════════════════

def _sync_musician_relations(musician: Musician, links: list[dict], contacts: list[dict]) -> None:
    """Reemplaza los links y contactos de un músico con los nuevos datos."""
    MusicianLink.query.filter_by(musician_id=musician.id).delete()
    MusicianContact.query.filter_by(musician_id=musician.id).delete()
    for d in links:
        db.session.add(MusicianLink(musician_id=musician.id, **d))
    for d in contacts:
        db.session.add(MusicianContact(musician_id=musician.id, **d))


def _parse_musician_contacts() -> list[dict]:
    """Parsea contactos dinámicos (email/phone/whatsapp) del formulario."""
    kinds  = request.form.getlist("contact_kind[]")
    values = request.form.getlist("contact_value[]")
    labels = request.form.getlist("contact_label[]")
    result = []
    for i, (kind, value) in enumerate(zip(kinds, values)):
        kind  = kind.strip()
        value = value.strip()
        label = labels[i].strip() if i < len(labels) else ""
        if kind and value:
            result.append({"kind": kind, "value": value, "label": label or None})
    return result


@bp_admin.route("/musicos")
@login_required
def musicians():
    _require_admin()
    items = Musician.query.order_by(Musician.name.asc()).all()
    return render_template("admin/musicians.html", musicians=items, form=AdminUserActionForm())


@bp_admin.route("/musicos/new", methods=["GET", "POST"])
@login_required
def musician_new():
    """Crear músico con links dinámicos de redes y contactos."""
    _require_admin()
    form = MusicianForm()
    if form.validate_on_submit():
        try:
            img = _save_image_simple(form.image.data)
            m = Musician(
                name=form.name.data.strip(),
                description=form.description.data.strip() if form.description.data else None,
                image_path=img,
                active=form.active.data,
            )
            db.session.add(m)
            db.session.flush()

            links    = _parse_dynamic_links("link")
            contacts = _parse_musician_contacts()
            _sync_musician_relations(m, links, contacts)

            db.session.commit()
            flash(f"✅ Músico «{m.name}» agregado.", "success")
            return redirect(url_for("admin.musicians"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo guardar el músico. Error: {e}", "error")

    return render_template("admin/musician_form.html", form=form,
                           title="Nuevo músico",
                           platforms=MUSICIAN_PLATFORMS,
                           contact_kinds=MUSICIAN_CONTACT_KINDS)


@bp_admin.route("/musicos/<int:musician_id>/edit", methods=["GET", "POST"])
@login_required
def musician_edit(musician_id):
    """Editar músico con links y contactos dinámicos."""
    _require_admin()
    m    = Musician.query.get_or_404(musician_id)
    form = MusicianForm(obj=m)
    if form.validate_on_submit():
        try:
            m.name        = form.name.data.strip()
            m.description = form.description.data.strip() if form.description.data else None
            m.active      = form.active.data
            if form.image.data and form.image.data.filename:
                m.image_path = _save_image_simple(form.image.data)

            links    = _parse_dynamic_links("link")
            contacts = _parse_musician_contacts()
            _sync_musician_relations(m, links, contacts)

            db.session.commit()
            flash(f"✅ Músico «{m.name}» actualizado.", "success")
            return redirect(url_for("admin.musicians"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ No se pudo actualizar el músico. Error: {e}", "error")

    return render_template("admin/musician_form.html", form=form,
                           title=f"Editar — {m.name}", musician=m,
                           platforms=MUSICIAN_PLATFORMS,
                           contact_kinds=MUSICIAN_CONTACT_KINDS)


@bp_admin.post("/musicos/<int:musician_id>/delete")
@login_required
def musician_delete(musician_id):
    _require_admin()
    form = AdminUserActionForm()
    if not form.validate_on_submit():
        flash("Solicitud inválida.", "error"); return redirect(url_for("admin.musicians"))
    m = Musician.query.get_or_404(musician_id)
    db.session.delete(m); db.session.commit()
    flash(f"Músico «{m.name}» eliminado.", "info")
    return redirect(url_for("admin.musicians"))
