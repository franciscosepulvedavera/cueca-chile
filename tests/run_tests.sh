#!/usr/bin/env bash
# =============================================================================
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
#   ./run_tests.sh --no-report       → no abrir el reporte al finalizar
#
# Al terminar abre automáticamente el reporte HTML en el navegador.
# El reporte queda guardado en:  tests/reports/report.html
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.test"
REPORT_FILE="$SCRIPT_DIR/reports/report.html"
MARKER=""
KEYWORD=""
OPEN_REPORT=true

# ── Colores ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   🎶  Cueca Chile — Test Runner          ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Verificar .env.test ───────────────────────────────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
  echo -e "${RED}✗  No se encontró $ENV_FILE${NC}"
  echo -e "   Copia el ejemplo y edita tus credenciales:"
  echo -e "   ${YELLOW}cp tests/.env.test.example tests/.env.test${NC}"
  exit 1
fi

# Cargar variables de entorno
set -a
source "$ENV_FILE"
set +a

echo -e "  ${GREEN}✓${NC}  Entorno cargado"
echo -e "  ${CYAN}URL:${NC}       ${BASE_URL:-http://127.0.0.1:5000}"
echo -e "  ${CYAN}Navegador:${NC} ${BROWSER:-chromium}  │  ${CYAN}Headless:${NC} ${HEADLESS:-true}"
echo ""

# ── Verificar servidor ────────────────────────────────────────────────────────
echo -e "${BOLD}Verificando servidor Flask...${NC}"
if ! curl -s --max-time 4 "${BASE_URL:-http://127.0.0.1:5000}" > /dev/null 2>&1; then
  echo -e "${RED}✗  El servidor no responde en ${BASE_URL:-http://127.0.0.1:5000}${NC}"
  echo -e "   Levántalo en otra terminal:  ${YELLOW}flask run${NC}"
  exit 1
fi
echo -e "  ${GREEN}✓${NC}  Servidor activo"
echo ""

# ── Parsear argumentos ────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --visible)
      export HEADLESS=false
      echo -e "  ${YELLOW}⚠  Modo visible — se abrirá el navegador durante los tests${NC}"
      ;;
    --no-report)
      OPEN_REPORT=false
      ;;
    auth|admin|publico)
      MARKER="$arg"
      ;;
    *)
      KEYWORD="$arg"
      ;;
  esac
done

# ── Crear directorio de reportes ──────────────────────────────────────────────
mkdir -p "$SCRIPT_DIR/reports"

# ── Construir comando pytest ──────────────────────────────────────────────────
PYTEST_CMD="pytest"

if [[ -n "$MARKER" ]]; then
  PYTEST_CMD="$PYTEST_CMD -m $MARKER"
  echo -e "  ${CYAN}Filtro marker:${NC}  $MARKER"
fi

if [[ -n "$KEYWORD" ]]; then
  PYTEST_CMD="$PYTEST_CMD -k \"$KEYWORD\""
  echo -e "  ${CYAN}Filtro nombre:${NC}  $KEYWORD"
fi

echo ""
echo -e "${BOLD}Ejecutando:${NC} ${DIM}$PYTEST_CMD${NC}"
echo -e "${CYAN}────────────────────────────────────────────${NC}"
echo ""

# ── Cambiar al directorio de tests y ejecutar ─────────────────────────────────
cd "$SCRIPT_DIR"
eval "$PYTEST_CMD"
STATUS=$?

# ── Resultado en consola ──────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}────────────────────────────────────────────${NC}"
if [[ $STATUS -eq 0 ]]; then
  echo -e "  ${GREEN}${BOLD}✓  Todos los tests pasaron${NC}"
else
  echo -e "  ${RED}${BOLD}✗  Algunos tests fallaron  (exit code: $STATUS)${NC}"
fi

# ── Abrir reporte HTML ────────────────────────────────────────────────────────
echo ""
if [[ -f "$REPORT_FILE" ]]; then
  echo -e "  ${CYAN}📄 Reporte:${NC} $REPORT_FILE"
  if $OPEN_REPORT; then
    echo -e "  ${DIM}   Abriendo en el navegador...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
      open "$REPORT_FILE"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "$REPORT_FILE"
    elif command -v wslview &> /dev/null; then
      wslview "$REPORT_FILE"
    else
      echo -e "  ${YELLOW}   Abre manualmente el archivo de arriba.${NC}"
    fi
  else
    echo -e "  ${DIM}   (usa --no-report para no abrir automáticamente)${NC}"
  fi
fi
echo ""

exit $STATUS
