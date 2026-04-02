#!/usr/bin/env bash
# =============================================================================
# scripts/deploy.sh — Deploy seguro a Railway con respaldo de imágenes
#
# Uso desde la raíz del proyecto:
#   ./scripts/deploy.sh
#
# Qué hace:
#   1. Descarga todas las imágenes actuales de producción → static/uploads/
#   2. Hace git push con los cambios de código
#   3. Despliega con `railway up` (que incluye las imágenes gracias a .railwayignore)
#
# Requisitos:
#   - railway CLI instalado y autenticado (railway login)
#   - curl instalado
#   - git configurado
# =============================================================================

set -euo pipefail

PROD_URL="${PROD_URL:-https://cueca-chile-production.up.railway.app}"
UPLOADS_DIR="static/uploads"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo ""
echo -e "${BOLD}${CYAN}┌─────────────────────────────────────────┐${NC}"
echo -e "${BOLD}${CYAN}│  🎶  Cueca Chile — Deploy con respaldo   │${NC}"
echo -e "${BOLD}${CYAN}└─────────────────────────────────────────┘${NC}"
echo ""

# ── PASO 1: Verificar conexión con producción ─────────────────────────────────
echo -e "${BOLD}[1/4] Verificando conexión con producción...${NC}"
if ! curl -s --max-time 5 "$PROD_URL" > /dev/null; then
  echo -e "${YELLOW}⚠ No se pudo conectar a $PROD_URL. Se omite el respaldo de imágenes.${NC}"
  SKIP_BACKUP=true
else
  echo -e "  ${GREEN}✓${NC} Producción accesible en $PROD_URL"
  SKIP_BACKUP=false
fi
echo ""

# ── PASO 2: Descargar imágenes de producción ──────────────────────────────────
if [ "$SKIP_BACKUP" = false ]; then
  echo -e "${BOLD}[2/4] Descargando imágenes desde producción...${NC}"
  mkdir -p "$UPLOADS_DIR"

  # Obtener todas las rutas de imágenes desde el HTML del sitio
  IMAGEN_PATHS=$(curl -s "$PROD_URL/campeonatos/" "$PROD_URL/creadores/" "$PROD_URL/tiendas/" "$PROD_URL/musicos/" "$PROD_URL/" 2>/dev/null \
    | grep -oE 'uploads/[a-zA-Z0-9_\-\.]+\.(jpg|jpeg|png|webp|gif)' \
    | sort -u)

  COUNT=0
  SKIP=0
  for IMG_PATH in $IMAGEN_PATHS; do
    FILENAME=$(basename "$IMG_PATH")
    LOCAL_PATH="$UPLOADS_DIR/$FILENAME"

    # Solo descargar si no existe ya localmente
    if [ -f "$LOCAL_PATH" ]; then
      SKIP=$((SKIP + 1))
      continue
    fi

    HTTP_CODE=$(curl -s -o "$LOCAL_PATH" -w "%{http_code}" "$PROD_URL/static/$IMG_PATH")
    if [ "$HTTP_CODE" = "200" ]; then
      echo -e "  ${GREEN}↓${NC} $FILENAME"
      COUNT=$((COUNT + 1))
    else
      rm -f "$LOCAL_PATH"
    fi
  done

  if [ $COUNT -gt 0 ] || [ $SKIP -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} $COUNT descargadas, $SKIP ya existían localmente"
  else
    echo -e "  ${YELLOW}⚠${NC} No se encontraron imágenes para descargar"
  fi
else
  echo -e "${BOLD}[2/4] Respaldo omitido (sin conexión a producción)${NC}"
fi
echo ""

# ── PASO 3: Git push (código sin imágenes) ────────────────────────────────────
echo -e "${BOLD}[3/4] Subiendo código a GitHub...${NC}"
if git diff --quiet && git diff --cached --quiet; then
  echo -e "  ${YELLOW}⚠${NC} No hay cambios en el código para commitear"
else
  git add -A
  echo -e "  Archivos a commitear:"
  git status --short | head -20
  read -p "  ¿Mensaje del commit? (Enter para usar 'chore: deploy'): " MSG
  MSG="${MSG:-chore: deploy}"
  git commit -m "$MSG"
fi
git push origin main
echo -e "  ${GREEN}✓${NC} Código pusheado a GitHub"
echo ""

# ── PASO 4: railway up (código + imágenes) ────────────────────────────────────
echo -e "${BOLD}[4/4] Desplegando a Railway (incluye imágenes)...${NC}"
railway up --service cueca-chile --detach
echo -e "  ${GREEN}✓${NC} Deploy iniciado en Railway"
echo ""
echo -e "${GREEN}${BOLD}✓ Deploy completado${NC}"
echo -e "  Sitio: ${CYAN}$PROD_URL${NC}"
echo ""
