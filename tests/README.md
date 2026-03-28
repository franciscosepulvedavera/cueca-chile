# Cueca Chile — Suite de Pruebas E2E

Suite de pruebas de extremo a extremo (End-to-End) para la plataforma [Cueca Chile](https://github.com/franciscosepulvedavera/cueca-chile), construida con **pytest-bdd** (Gherkin/BDD) y **Playwright** (automatización de navegador).

---

## Descripción del Proyecto

**Cueca Chile** es una plataforma colaborativa para la comunidad cuequera chilena. Permite:

- Publicar y consultar **eventos** de cueca (campeonatos, clases, peñas)
- Consultar **campeonatos nacionales** con su cuadro de honor por año y categoría
- Ver la **tabla de resultados** nacional por región (1°, 2°, 3° y 4° lugar)
- Directorio de **creadores de contenido** (YouTube, Instagram, TikTok)
- Directorio de **tiendas** de ropa y accesorios de cueca
- Panel de **administración** para gestionar todos los recursos anteriores

La suite de pruebas cubre todos estos módulos tanto en sus vistas públicas como en el panel admin.

---

## Estructura del Proyecto de Pruebas

```
tests/
│
├── README.md                        ← este archivo
├── pytest.ini                       ← configuración de pytest y pytest-bdd
├── conftest.py                      ← fixtures globales (browser, admin_page, anon_page)
├── requirements-test.txt            ← dependencias de la suite
├── .env.test                        ← variables de entorno LOCALES (no se sube a git)
├── .env.test.example                ← plantilla de configuración (sí se sube a git)
│
├── features/                        ← escenarios en Gherkin (.feature)
│   ├── auth.feature                 ← login, logout, registro
│   ├── eventos.feature              ← listado, detalle, crear evento
│   ├── campeonatos.feature          ← listado, detalle, cuadro de honor, filtros
│   ├── creadores.feature            ← directorio de creadores
│   ├── tiendas.feature              ← directorio de tiendas
│   ├── resultados.feature           ← tabla de resultados por región
│   └── admin/
│       ├── admin_campeonatos.feature ← CRUD campeonatos + honor entries
│       ├── admin_honor.feature       ← agregar/editar/eliminar entradas honor
│       ├── admin_creadores.feature   ← CRUD creadores de contenido
│       ├── admin_tiendas.feature     ← CRUD tiendas
│       └── admin_resultados.feature  ← gestión y filtros de resultados
│
└── step_defs/                       ← implementaciones Python de los steps
    ├── test_auth.py
    ├── test_eventos.py
    ├── test_campeonatos.py
    ├── test_creadores.py
    ├── test_tiendas.py
    ├── test_resultados.py
    └── admin/
        ├── test_admin_campeonatos.py
        ├── test_admin_honor.py
        ├── test_admin_creadores.py
        ├── test_admin_tiendas.py
        └── test_admin_resultados.py
```

### Qué hace cada capa

| Capa | Rol |
|---|---|
| `features/*.feature` | Especificación legible en Gherkin — describe el comportamiento esperado |
| `step_defs/test_*.py` | Implementación Python de cada `Given / When / Then` usando Playwright |
| `conftest.py` | Fixtures de sesión: abre el browser, inyecta `base_url`, realiza login admin |
| `pytest.ini` | Apunta `testpaths` a `step_defs/` y `bdd_features_base_dir` a `features/` |

---

## Tecnologías

| Herramienta | Versión | Propósito |
|---|---|---|
| Python | 3.11+ | Lenguaje base |
| pytest | 8.x | Runner de tests |
| pytest-bdd | 7.3 | Integración Gherkin con pytest |
| pytest-playwright | 0.5.1 | Fixtures de Playwright para pytest |
| Playwright | 1.x | Automatización de Chromium headless |

---

## Requisitos Previos

1. **Python 3.11+** instalado
2. **pip** disponible
3. El **servidor de la aplicación** debe estar corriendo y accesible desde la máquina que ejecuta las pruebas
4. Debe existir un **usuario administrador** en la base de datos

---

## Instalación

```bash
# Desde la raíz del repositorio, entrar a la carpeta tests
cd tests

# Instalar dependencias de prueba
pip install -r requirements-test.txt

# Instalar el browser Chromium (solo la primera vez)
playwright install chromium
```

---

## Configuración

### Variables de Entorno

Copiar la plantilla y editar los valores:

```bash
cp .env.test.example .env.test
```

Contenido de `.env.test`:

```env
# URL base del sitio a probar
BASE_URL=http://127.0.0.1:5000

# Credenciales del administrador
ADMIN_EMAIL=admin@admin.cl
ADMIN_PASSWORD=admin1234

# Modo headless: true = sin ventana (CI), false = con ventana (debug)
HEADLESS=true

# Browser a usar (chromium, firefox, webkit)
BROWSER=chromium
```

### Entorno Local vs Producción

| Variable | Local (dev) | Producción (Railway) |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:5000` | `https://tu-dominio.railway.app` |
| `ADMIN_EMAIL` | email del admin en `.env` local | email del admin en Railway |
| `ADMIN_PASSWORD` | contraseña del admin local | contraseña en Railway |
| `HEADLESS` | `false` para debug, `true` para CI | `true` siempre |

> **Importante:** `.env.test` está en `.gitignore` y nunca se sube al repositorio. Usar `.env.test.example` como referencia.

---

## Cómo Ejecutar las Pruebas

Las pruebas se ejecutan desde la carpeta `tests/`:

```bash
cd tests
```

### Ejecutar toda la suite

```bash
# Cargando variables desde .env.test
export $(cat .env.test | xargs) && pytest
```

O si usas `python-dotenv` o `direnv`, simplemente:

```bash
pytest
```

### Ejecutar un módulo específico

```bash
# Solo pruebas de autenticación
pytest step_defs/test_auth.py

# Solo pruebas del panel admin
pytest step_defs/admin/

# Solo pruebas públicas (no admin)
pytest step_defs/test_campeonatos.py step_defs/test_creadores.py
```

### Ejecutar un escenario específico por nombre

```bash
pytest -k "test_login_exitoso"
pytest -k "campeonato"
pytest -k "eliminar"
```

### Ejecutar con navegador visible (modo debug)

```bash
HEADLESS=false pytest step_defs/test_auth.py -v
```

### Ejecutar con salida detallada

```bash
pytest -v --tb=long
```

### Ejecutar solo los tests que fallaron en el último run

```bash
pytest --lf
```

### Ejecutar en paralelo (requiere pytest-xdist)

```bash
pytest -n 4
```

---

## Marcadores Disponibles

Los tests se pueden filtrar por marcador (definidos en `pytest.ini`):

| Marcador | Descripción |
|---|---|
| `publico` | Vistas públicas sin autenticación |
| `admin` | Panel de administración |
| `auth` | Flujos de autenticación |

```bash
pytest -m admin
pytest -m "publico and not auth"
```

---

## Escenarios Cubiertos

### Autenticación (`auth.feature`) — 6 escenarios
- ✅ Login exitoso como administrador
- ✅ Login fallido con contraseña incorrecta
- ✅ Login fallido con email inexistente
- ✅ Registro exitoso de nuevo usuario
- ✅ Registro fallido con email ya registrado
- ✅ Logout exitoso

### Eventos (`eventos.feature`) — 5 escenarios
- ✅ Ver lista de eventos sin login
- ✅ Acceder al formulario de nuevo evento requiere login
- ✅ Ver formulario autenticado
- ✅ Crear evento como administrador
- ✅ Ver detalle de un evento aprobado

### Campeonatos (`campeonatos.feature`) — 6 escenarios
- ✅ Ver lista de campeonatos activos
- ✅ Ver detalle con cuadro de honor
- ✅ Filtrar cuadro de honor por año
- ✅ Ver íconos de redes sociales
- ✅ Ver región y comuna de ganadores
- ✅ Ver badge de pareja más popular

### Creadores (`creadores.feature`) — 5 escenarios
- ✅ Ver directorio de creadores
- ✅ Tarjeta con URL principal
- ✅ Tarjeta con redes sociales sin URL
- ✅ Ver nombre y descripción
- ✅ Creadores inactivos no aparecen

### Tiendas (`tiendas.feature`) — 5 escenarios
- ✅ Ver directorio de tiendas
- ✅ Tienda con sitio web
- ✅ Tienda con dirección física
- ✅ Tienda con redes sociales
- ✅ Tiendas inactivas no aparecen

### Resultados (`resultados.feature`) — 5 escenarios
- ✅ Ver tabla de resultados completa
- ✅ Tabla tiene todas las columnas de posición (1°–4°)
- ✅ Ver las 16 regiones de Chile en orden norte–sur
- ✅ Regiones sin resultados muestran guión
- ✅ Ver totales por región

### Admin — Campeonatos (`admin_campeonatos.feature`) — 6 escenarios
- ✅ Ver lista en el panel admin
- ✅ Crear campeonato nuevo
- ✅ Editar campeonato existente
- ✅ Eliminar campeonato
- ✅ Acceso denegado a usuario no autenticado
- ✅ Validación de campos requeridos

### Admin — Cuadro de Honor (`admin_honor.feature`) — 7 escenarios
- ✅ Agregar entrada de 1° lugar
- ✅ Agregar pareja más popular (posición especial)
- ✅ Agregar entrada de 4° lugar
- ✅ Agregar entrada con redes sociales
- ✅ Agregar entrada con región y comuna
- ✅ Editar entrada existente
- ✅ Eliminar entrada

### Admin — Creadores (`admin_creadores.feature`) — 6 escenarios
- ✅ Ver lista en panel admin
- ✅ Crear creador con URL
- ✅ Crear creador sin URL (campo opcional)
- ✅ Verificar que URL es opcional
- ✅ Editar creador
- ✅ Eliminar creador

### Admin — Tiendas (`admin_tiendas.feature`) — 6 escenarios
- ✅ Ver lista en panel admin
- ✅ Crear tienda con dirección física
- ✅ Crear tienda con redes sociales
- ✅ Crear tienda con número WhatsApp
- ✅ Editar tienda
- ✅ Eliminar tienda

### Admin — Resultados (`admin_resultados.feature`) — 8 escenarios
- ✅ Ver gestión de resultados
- ✅ Badge de pareja más popular
- ✅ Badge de cuarto lugar
- ✅ Filtrar por campeonato
- ✅ Filtrar por año
- ✅ Limpiar filtros
- ✅ Editar entrada desde resultados
- ✅ Eliminar entrada desde resultados

**Total: 65 escenarios — 57 passing, 8 skipped (datos opcionales no disponibles)**

---

## Tests Skipped

Los tests marcados como `skipped` no son errores — se saltan automáticamente cuando el sistema no tiene los datos necesarios para validar ese escenario. Por ejemplo:

- "No hay campeonatos con entradas en el cuadro de honor"
- "No hay entradas de cuarto lugar en el sistema"
- "Se necesitan al menos 2 campeonatos para filtrar"

Para que estos tests pasen, solo hay que cargar los datos correspondientes desde el panel admin.

---

## Integración con CI/CD (Railway / GitHub Actions)

Para ejecutar en Railway o en GitHub Actions, configurar las variables de entorno en el entorno de CI:

```yaml
# Ejemplo: .github/workflows/tests.yml
env:
  BASE_URL: ${{ secrets.PRODUCTION_URL }}
  ADMIN_EMAIL: ${{ secrets.ADMIN_EMAIL }}
  ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
  HEADLESS: "true"
```

---

## Troubleshooting

### El servidor no responde
```
playwright._impl._errors.TimeoutError: page.goto: Timeout
```
→ Verificar que `BASE_URL` apunta a un servidor corriendo y accesible.

### Login falla en admin
```
AssertionError: '/admin/campeonatos' in 'http://.../auth/login?next=...'
```
→ Las credenciales `ADMIN_EMAIL` / `ADMIN_PASSWORD` son incorrectas o el usuario no tiene rol admin.

### Chromium no instalado
```
Error: browserType.launch: Executable doesn't exist
```
→ Ejecutar `playwright install chromium`.

### Tests fallan por datos inexistentes
→ Crear datos de prueba desde el panel admin antes de ejecutar (`/admin/campeonatos`, `/admin/creadores`, etc.).
