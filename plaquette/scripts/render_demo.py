#!/usr/bin/env python3
"""Génère les captures démo (projet fictif) via Chromium headless."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
OUT = ROOT / "assets" / "processed" / "demo"

SCREENS = [
    ("01-bandeau.html", "01-bandeau-capture-idee.png", 1024, 49),
    ("02-gestion-projets.html", "02-gestion-projets.png", 1024, 747),
    ("03-roadmap.html", "03-roadmap.png", 1024, 749),
    ("04-facettes.html", "04-facettes.png", 1024, 567),
]


def find_chromium() -> str:
    for cmd in ("chromium", "google-chrome", "chromium-browser"):
        path = shutil.which(cmd)
        if path:
            return path
    raise SystemExit("Chromium introuvable")


def render(html: str, out: Path, w: int, h: int, chromium: str) -> None:
    url = f"file://{DEMO / html}"
    subprocess.run(
        [
            chromium,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            f"--window-size={w},{h}",
            f"--screenshot={out}",
            url,
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    chromium = find_chromium()
    for html, png, w, h in SCREENS:
        dest = OUT / png
        render(html, dest, w, h, chromium)
        print(f"  {png}")
    print(f"Captures démo → {OUT}")


if __name__ == "__main__":
    main()
