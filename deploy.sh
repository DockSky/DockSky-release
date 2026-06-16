#!/bin/bash
# Deploy docs.docksky.fr (Docusaurus statique → nginx docksky_docs)
#
# Usage :
#   ./deploy.sh              build local + rsync immédiat sur le VPS
#   ./deploy.sh --push-only  push GitHub → le workflow CI build + déploie
#   ./deploy.sh --first-time clone le repo sur le VPS (une seule fois)

set -euo pipefail

REMOTE="git@github.com:DockSky/DockSky-release.git"
VPS_DIR="/home/debian/docker/docksky-docs"
CONTAINER="docksky_docs"

echo "=== DockSky Docs — Deploy ==="

if [[ "${1:-}" == "--push-only" ]]; then
  echo "[1/1] Push vers GitHub (GitHub Actions déploiera sur docs.docksky.fr)..."
  git push origin main
  echo "Suivre le workflow : https://github.com/DockSky/DockSky-release/actions"
  exit 0
fi

if [[ "${1:-}" == "--first-time" ]]; then
  echo "[SETUP] Clone du repo sur le VPS..."
  ssh docksky-vps "
    docker stop $CONTAINER 2>/dev/null || true
    mv $VPS_DIR ${VPS_DIR}_backup_\$(date +%Y%m%d) 2>/dev/null || true
    git clone $REMOTE $VPS_DIR
    cd $VPS_DIR && docker compose up -d
  "
  echo "Setup terminé. Lance ./deploy.sh pour publier le build."
  exit 0
fi

echo "[1/3] Build Docusaurus..."
npm run build

echo "[2/3] Rsync build/ vers VPS..."
rsync -az --delete build/ "docksky-vps:${VPS_DIR}/build/"

echo "[3/3] Vérification conteneur..."
ssh docksky-vps "docker ps --filter name=$CONTAINER --format 'Status: {{.Status}}'"

echo ""
echo "=== Deploy terminé ! https://docs.docksky.fr ==="
echo "Astuce : avec les secrets GitHub configurés, un simple 'git push' suffit (./deploy.sh --push-only)."
