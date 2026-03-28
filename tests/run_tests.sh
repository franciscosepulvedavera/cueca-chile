#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_tests.sh — Ejecutar la suite de pruebas Cueca Chile
#
# Uso:
#   ./run_tests.sh                   → toda la suite
#   ./run_tests.sh auth              → solo tests de autenticación
#   ./run_tests.sh admin             → solo tests de administración
#   ./run_tests.sh publico           → solo tests públicos
#   ./run_tests.sh "test_login"      → tests que contengan esa palabra
#   ./run_tests.sh --visible         → abre el navegador (modo no headless)
#   ./run_tests.sh auth --visible    → filtro + navegador visible
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.test"
MARKER=""
KEYWORD=""
EXTRA_ARGS=""

# ── Colores ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Banner ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}┌──────────────────────────────────────────┐${NC}"
echo -e "${BOLD}${CYAN}│   🎶  Cueca Chile — Test Runner           │${NC}"
echo -e "${BOLD}${CYAN}└──────────────────────────────────────────┘${NC}"
echo ""

# ── Verificar .env.test ───────────────────────────────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
  echo -e "${RED}✗ No se encontró $ENV_FILE${NC}"
  echo -e "  Copia el ejemplo y edita tus credenciales:"
  echo -e "  ${YELLOW}cp tests/.env.test.example tests/.env.test${NC}"
  exit 1
fi

# Cargar variables de entorno
set -a
source "$ENV_FILE"
set +a

echo -e "  ${GREEN}✓${NC} Entorno cargado desde .env.test"
echo -e "  ${CYAN}→ BASE_URL:${NC}  ${BASE_URL:-http://127.0.0.1:5000}"
echo -e "  ${CYAN}→ HEADLESS:${NC}  ${HEADLESS:-true}"
echo -e "  ${CYAN}→ BROWSER:${NC}   ${BROWSER:-chromium}"
echo ""

# ── Verificar que el servidor está corriendo ──────────────────────────────────
echo -e "${BOLD}Verificando servidor Flask...${NC}"
if ! curl -s --max-time 3 "${BASE_URL:-http://127.0.0.1:5000}" > /dev/null; then
  echo -e "${RED}✗ El servidor no responde en ${BASE_URL:-http://127.0.0.1:5000}${NC}"
  echo -e "  Levántalo en otra terminal con: ${YELLOW}flask run${NC}"
  exit 1
fi
echo -e "  ${GREEN}✓${NC} Servidor activo en ${BASE_URL:-http://127.0.0.1:5000}"
echo ""

# ── Parsear argumentos ────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --visible)
      export HEADLESS=false
      echo -e "  ${YELLOW}⚠ Modo visible activado — se abrirá el navegador${NC}"
      ;;
    auth|admin|publico)
      MARKER="$arg"
      ;;
    *)
      KEYWORD="$arg"
      ;;
  esac
done

# ── Construir comando pytest ──────────────────────────────────────────────────
PYTEST_CMD="pytest -v --tb=short"

if [[ -n "$MARKER" ]]; then
  PYTEST_CMD="$PYTEST_CMD -m $MARKER"
  echo -e "  ${CYAN}Filtro por marker:${NC} $MARKER"
fi

if [[ -n "$KEYWORD" ]]; then
  PYTEST_CMD="$PYTEST_CMD -k \"$KEYWORD\""
  echo -e "  ${CYAN}Filtro por nombre:${NC} $KEYWORD"
fi

echo ""
echo -e "${BOLD}Ejecutando:${NC} $PYTEST_CMD"
echo -e "${CYAN}────────────────────────────────────────────${NC}"
echo ""

# ── Cambiar al directorio de tests y ejecutar ─────────────────────────────────
cd "$SCRIPT_DIR"
eval "$PYTEST_CMD"
STATUS=$?

# ── Resultado final ───────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}────────────────────────────────────────────${NC}"
if [[ $STATUS -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}✓ Todos los tests pasaron${NC}"
else
  echo -e "${RED}${BOLD}✗ Algunos tests fallaron (exit code: $STATUS)${NC}"
fi
echo ""

exit $STATUS
