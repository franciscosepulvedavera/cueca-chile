# 🎵 Cueca Chile — Plataforma de Eventos y Contenido

Plataforma web colaborativa para la comunidad de la cueca chilena. Permite publicar y descubrir eventos, campeonatos nacionales, creadores de contenido y tiendas especializadas.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Local](#instalación-local)
- [Variables de Entorno](#variables-de-entorno)
- [Migraciones y Base de Datos](#migraciones-y-base-de-datos)
- [Levantar el Servidor](#levantar-el-servidor)
- [Roles y Permisos](#roles-y-permisos)
- [Deploy en Producción](#deploy-en-producción)
- [Errores Comunes](#errores-comunes)

---

## Descripción

Cueca Chile es una aplicación web full-stack construida con Flask. Centraliza la información del ecosistema cuequero en cinco secciones principales:

| Sección | Descripción |
|---|---|
| **Eventos** | Listado de eventos (regionales, nacionales, cuecazos, etc.) con filtros y paginación |
| **Campeonatos** | Directorio de campeonatos nacionales con cuadro de honor por año y categoría |
| **Creadores** | Directorio de canales y perfiles de contenido de cueca |
| **Tiendas** | Directorio de tiendas especializadas |
| **Resultados** | Tabla de posiciones acumuladas por región de Chile |

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | Flask 3 |
| ORM | SQLAlchemy 2 + Flask-SQLAlchemy |
| Migraciones | Flask-Migrate (Alembic) |
| Autenticación | Flask-Login |
| Formularios + CSRF | Flask-WTF + WTForms |
| Base de datos (prod) | PostgreSQL 14 |
| Base de datos (dev) | SQLite (alternativa) |
| Procesamiento de imágenes | Pillow |
| Tareas programadas | Flask-APScheduler |
| Variables de entorno | python-dotenv |
| Templating | Jinja2 |
| Frontend | HTML/CSS puro (Inter font, CSS Variables, Glassmorphism) |

---

## Estructura del Proyecto

```
cueca_site/
│
├── app.py                    # Fábrica de la aplicación (create_app)
├── config.py                 # Configuración centralizada (lee .env)
├── extensions.py             # Instancias de extensiones Flask
├── models.py                 # Modelos SQLAlchemy (User, Event, etc.)
├── forms.py                  # Formularios Flask-WTF
├── utils.py                  # Helpers: notify(), notify_staff()
├── seeds.py                  # Crea el admin inicial desde .env
│
├── blueprints/               # Módulos de rutas organizados por dominio
│   ├── auth.py               # /auth/ — registro, login, logout
│   ├── events.py             # /events/ — CRUD eventos + moderación
│   ├── admin.py              # /admin/ — panel completo de administración
│   ├── notifications.py      # /notifications/ — notificaciones in-app
│   ├── championships.py      # /campeonatos/ — campeonatos (público)
│   ├── creators.py           # /creadores/ — creadores (público)
│   ├── stores.py             # /tiendas/ — tiendas (público)
│   └── results.py            # /resultados/ — tabla de resultados
│
├── templates/                # Plantillas Jinja2
│   ├── base.html             # Layout base con navbar, flash, footer
│   ├── index.html            # Homepage con filtros y paginación
│   ├── _pagination.html      # Componente reutilizable de paginación
│   ├── auth/                 # login.html, register.html
│   ├── events/               # new.html, show.html, moderation.html
│   ├── notifications/        # index.html
│   ├── championships/        # index.html, show.html
│   ├── creators/             # index.html
│   ├── stores/               # index.html
│   ├── results/              # index.html
│   └── admin/                # users.html, championships.html,
│                             # championship_form.html, honor_form.html,
│                             # creators.html, creator_form.html,
│                             # stores.html, store_form.html
│
├── static/
│   ├── uploads/              # Imágenes subidas por usuarios (gitignoreado)
│   └── img/
│       └── background.png    # Imagen decorativa del fondo
│
├── migrations/               # Migraciones Alembic (gestionadas por Flask-Migrate)
├── .env                      # Variables de entorno (NO subir a git)
├── .gitignore
└── requirements.txt          # Dependencias del proyecto
```

---

## Requisitos Previos

- Python 3.11 o superior
- PostgreSQL 14+ (recomendado) o SQLite (desarrollo rápido)
- pip
- Git

### Verificar versiones

```bash
python3 --version   # Python 3.11+
psql --version      # PostgreSQL 14+
pip --version
```

---

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/cueca_site.git
cd cueca_site
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar manualmente:

```bash
pip install flask flask-sqlalchemy flask-migrate flask-login flask-wtf \
            flask-apscheduler pillow python-dotenv psycopg2-binary email-validator
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env   # si existe
# o crear manualmente (ver sección Variables de Entorno)
```

### 5. Crear la base de datos en PostgreSQL

```bash
# Iniciar el servicio de PostgreSQL
brew services start postgresql@14       # macOS con Homebrew
# sudo service postgresql start         # Linux

# Crear la base de datos
createdb cueca_db
```

### 6. Ejecutar migraciones

```bash
flask db upgrade
```

### 7. Crear el administrador inicial

```bash
python seeds.py
```

---

## Variables de Entorno

Crear el archivo `.env` en la raíz con el siguiente contenido:

```env
# ── Seguridad ─────────────────────────────────────────
# Clave para firmar cookies de sesión y tokens CSRF.
# En producción usar un valor largo y aleatorio:
#   python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=cambia-esto-en-produccion

# ── Base de datos ──────────────────────────────────────
# PostgreSQL (recomendado para producción)
DATABASE_URL=postgresql://tu_usuario@localhost:5432/cueca_db

# SQLite (alternativa para desarrollo rápido)
# DATABASE_URL=sqlite:///cueca.db

# ── Imágenes (formato Historia Instagram 9:16) ─────────
IMAGE_STD_WIDTH=1080
IMAGE_STD_HEIGHT=1920

# ── Administrador inicial (usado solo en seeds.py) ─────
ADMIN_EMAIL=admin@tusitio.cl
ADMIN_PASSWORD=una_contrasena_segura
ADMIN_NAME=Administrador
```

---

## Migraciones y Base de Datos

```bash
# Crear una nueva migración tras modificar models.py
flask db migrate -m "descripcion del cambio"

# Aplicar migraciones pendientes
flask db upgrade

# Ver el historial de migraciones
flask db history

# Revertir la última migración (uso con cuidado)
flask db downgrade
```

---

## Levantar el Servidor

```bash
# Modo desarrollo (con recarga automática)
flask run --port=8080

# Con debug explícito
FLASK_DEBUG=1 flask run --port=8080

# Con Python directamente
python app.py
```

El sitio estará disponible en: **http://127.0.0.1:8080**

### Credenciales de acceso inicial

Definidas en `.env`:
- **Email:** valor de `ADMIN_EMAIL`
- **Contraseña:** valor de `ADMIN_PASSWORD`

---

## Roles y Permisos

| Acción | user | moderator | admin |
|---|:---:|:---:|:---:|
| Ver eventos públicos | ✅ | ✅ | ✅ |
| Publicar evento (requiere aprobación) | ✅ | ✅ | — |
| Publicar evento (aprobación automática) | — | — | ✅ |
| Aprobar / rechazar eventos | — | ✅ | ✅ |
| Eliminar eventos | — | ✅ | ✅ |
| Gestionar campeonatos y cuadro de honor | — | — | ✅ |
| Gestionar creadores de contenido | — | — | ✅ |
| Gestionar tiendas | — | — | ✅ |
| Gestionar usuarios (ban/rol/delete) | — | — | ✅ |

---

## Deploy en Producción

### Opción A — Railway (Recomendado, gratis)

1. Crear cuenta en [railway.app](https://railway.app)
2. Nuevo proyecto → "Deploy from GitHub repo"
3. Agregar servicio PostgreSQL en el mismo proyecto
4. En Variables de Entorno del proyecto configurar:
   ```
   SECRET_KEY=<valor largo y aleatorio>
   DATABASE_URL=<URL que Railway genera automáticamente>
   ADMIN_EMAIL=admin@tusitio.cl
   ADMIN_PASSWORD=<contraseña segura>
   FLASK_APP=app.py
   ```
5. Railway detecta Flask automáticamente. Agregar `Procfile`:
   ```
   web: flask db upgrade && gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
   ```
6. Agregar `gunicorn` al `requirements.txt`

### Opción B — Render (gratis con limitaciones)

1. Crear cuenta en [render.com](https://render.com)
2. New → Web Service → conectar repo de GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `flask db upgrade && gunicorn "app:create_app()" --bind 0.0.0.0:$PORT`
4. Agregar base de datos PostgreSQL desde el dashboard de Render
5. Configurar variables de entorno en "Environment"

### Consideraciones de seguridad para producción

- Usar una `SECRET_KEY` larga y aleatoria (nunca el valor por defecto)
- Configurar HTTPS (Railway y Render lo hacen automáticamente)
- No exponer el archivo `.env` (está en `.gitignore`)
- La carpeta `static/uploads/` debe persistir entre deploys (usar almacenamiento externo como Cloudinary o S3 si es necesario)
- Configurar `FLASK_DEBUG=0` o no definir la variable en producción

---

## Errores Comunes

### Error: `connection refused` al conectar PostgreSQL

```bash
# Verificar que el servicio esté corriendo
brew services list | grep postgresql   # macOS
sudo service postgresql status          # Linux

# Iniciar si está detenido
brew services start postgresql@14
```

### Error: `You have not agreed to the Xcode license` (macOS)

```bash
sudo xcodebuild -license accept
```

### Error: Port 5000 already in use (macOS)

El puerto 5000 lo usa AirPlay Receiver. Usar otro puerto:
```bash
flask run --port=8080
```

### Error: `libicui18n.XX.dylib not found`

```bash
brew reinstall postgresql@14
```

### Error: `No module named 'psycopg2'`

```bash
pip install psycopg2-binary
```

### Las comunas no aparecen en el formulario de evento

El campo `comuna` se carga dinámicamente por JavaScript según la región seleccionada. Verificar que JavaScript esté habilitado en el navegador.
