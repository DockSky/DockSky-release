#!/bin/bash
# Deploy docs.docksky.fr (Docusaurus statique → nginx docksky_docs)
#
# Usage :
#   ./deploy.sh              build local + rsync immédiat sur le VPS (+ sync git VPS)
#   ./deploy.sh --push-only  push GitHub → le workflow CI build + déploie
#   ./deploy.sh --git-only   git pull sur le VPS (après push, sans rsync)
#   ./deploy.sh --first-time clone le repo sur le VPS (une seule fois)
#
# Workflows :
#   A) git : commit docs/ + build/ → push → ./deploy.sh --git-only
#   B) rsync : commit + push d'abord → ./deploy.sh (rsync + reset git VPS)
#   Ne pas enchaîner rsync puis git pull sans reset : le rsync salit l'index Git du VPS.

set -euo pipefail

REMOTE="git@github.com:DockSky/DockSky-release.git"
VPS_DIR="/home/debian/docker/docksky-docs"
CONTAINER="docksky_docs"

sync_vps_git() {
  ssh docksky-vps "
    cd $VPS_DIR
    git fetch origin
    git reset --hard origin/main
    git status -sb
  "
}

echo "=== DockSky Docs — Deploy ==="

if [[ "${1:-}" == "--push-only" ]]; then
  echo "[1/1] Push vers GitHub (GitHub Actions déploiera sur docs.docksky.fr)..."
  git push origin main
  echo "Suivre le workflow : https://github.com/DockSky/DockSky-release/actions"
  exit 0
fi

if [[ "${1:-}" == "--git-only" ]]; then
  echo "[1/1] Sync git sur VPS (origin/main)..."
  sync_vps_git
  echo ""
  echo "=== Deploy terminé ! https://docs.docksky.fr ==="
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

if git rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
  AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  if [[ "$AHEAD" != "0" ]]; then
    echo "⚠️  $AHEAD commit(s) local(aux) non poussé(s). Push avant deploy pour aligner le VPS."
    echo "    git push origin main && ./deploy.sh"
    exit 1
  fi
fi

echo "[1/4] Build Docusaurus..."
npm run build

echo "[2/4] Rsync build/ vers VPS..."
rsync -az --delete build/ "docksky-vps:${VPS_DIR}/build/"

echo "[3/4] Sync git VPS (évite conflit rsync vs git pull)..."
sync_vps_git

echo "[4/4] Vérification conteneur..."
ssh docksky-vps "docker ps --filter name=$CONTAINER --format 'Status: {{.Status}}'"

echo ""
echo "=== Deploy terminé ! https://docs.docksky.fr ==="
echo "Astuce : workflow git seul → push puis ./deploy.sh --git-only"
