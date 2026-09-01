#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML="$ROOT/plaquette.html"
OUT="$ROOT/output/plaquette-docksky-a4.pdf"

python3 "$ROOT/scripts/prepare_assets.py"

CHROMIUM=""
for cmd in chromium google-chrome chromium-browser; do
  if command -v "$cmd" &>/dev/null; then
    CHROMIUM="$cmd"
    break
  fi
done

if [[ -z "$CHROMIUM" ]]; then
  echo "Erreur : chromium introuvable. Ouvrir plaquette.html dans un navigateur -> Imprimer -> PDF A4."
  exit 1
fi

"$CHROMIUM" \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=10000 \
  --print-to-pdf="$OUT" \
  --no-pdf-header-footer \
  "file://$HTML"

echo "PDF genere -> $OUT"
