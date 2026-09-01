#!/usr/bin/env python3
"""Prépare les captures pour la plaquette : masquage DEV, recadrage Flameshot, floutage sensible."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "screenshots"
OUT = ROOT / "assets" / "processed"
BRANDING = ROOT / "assets" / "branding"


def _fill_rect(im: Image.Image, box: tuple[int, int, int, int], color: tuple[int, ...] | None = None) -> None:
    x0, y0, x1, y1 = box
    if color is None:
        color = im.getpixel((max(0, x0 - 2), max(0, y0 + 2)))
    draw = ImageDraw.Draw(im)
    draw.rectangle(box, fill=color)


def _blur_rect(im: Image.Image, box: tuple[int, int, int, int], radius: int = 12) -> None:
    x0, y0, x1, y1 = box
    region = im.crop(box)
    region = region.filter(ImageFilter.GaussianBlur(radius=radius))
    im.paste(region, box)


def _crop_bottom(im: Image.Image, px: int) -> Image.Image:
    if px <= 0:
        return im
    w, h = im.size
    return im.crop((0, 0, w, max(1, h - px)))


def _detect_dev_badge_box(im: Image.Image) -> tuple[int, int, int, int] | None:
    """Repère le badge orange DEV à gauche du bandeau."""
    w, h = im.size
    xs: list[int] = []
    ys: list[int] = []
    limit_x = int(w * 0.25)
    for y in range(h):
        for x in range(limit_x):
            r, g, b = im.getpixel((x, y))
            if r > 200 and 80 < g < 160 and b < 60:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    pad = max(4, int(w * 0.004))
    return (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(w, max(xs) + pad + 1),
        min(h, max(ys) + pad + 1),
    )


def process_bandeau(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    box = _detect_dev_badge_box(im)
    if box:
        # Fond du bandeau autour du logo
        bg = im.getpixel((max(0, box[0] - 8), box[1] + 2))
        _fill_rect(im, box, bg)
    else:
        # repli proportionnel (ancienne résolution ~1024 px)
        w = im.size[0]
        scale = w / 1024
        _fill_rect(
            im,
            (int(118 * scale), int(2 * scale), int(168 * scale), int(22 * scale)),
        )
    im.save(dst, optimize=True)


def process_generic(src: Path, dst: Path, *, crop_bottom: int = 36) -> None:
    im = Image.open(src).convert("RGB")
    im = _crop_bottom(im, crop_bottom)
    im.save(dst, optimize=True)


def process_acces_ia(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    im = _crop_bottom(im, 40)
    # Flouter la liste des secrets (noms uniquement, pas les valeurs — jamais affichées)
    w, h = im.size
    _blur_rect(im, (int(w * 0.52), int(h * 0.58), w - 12, h - 55), radius=10)
    # Flouter la zone token / expiration en haut
    _blur_rect(im, (12, 55, w - 12, int(h * 0.42)), radius=8)
    im.save(dst, optimize=True)


def copy_logo() -> None:
    src = Path("/home/bob/projets/docksky-web/public/logos/logo-transparent.png")
    if src.exists():
        im = Image.open(src).convert("RGBA")
        im.thumbnail((280, 80), Image.Resampling.LANCZOS)
        BRANDING.mkdir(parents=True, exist_ok=True)
        im.save(BRANDING / "logo.png", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "recto").mkdir(exist_ok=True)
    (OUT / "verso").mkdir(exist_ok=True)
    copy_logo()

    process_bandeau(SRC / "recto" / "01-bandeau-capture-idee.png", OUT / "recto" / "01-bandeau-capture-idee.png")
    process_generic(SRC / "recto" / "02-gestion-projets.png", OUT / "recto" / "02-gestion-projets.png")
    process_generic(SRC / "recto" / "03-roadmap.png", OUT / "recto" / "03-roadmap.png")
    process_generic(SRC / "recto" / "04-facettes.png", OUT / "recto" / "04-facettes.png")
    process_generic(SRC / "verso" / "01-contextes-ia.png", OUT / "verso" / "01-contextes-ia.png")
    process_acces_ia(SRC / "verso" / "02-acces-ia-mcp.png", OUT / "verso" / "02-acces-ia-mcp.png")

    print(f"Assets traités → {OUT}")


if __name__ == "__main__":
    main()
