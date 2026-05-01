#!/usr/bin/env python3
"""
Regenerate the PWA / iOS home-screen icons in ../icons/.

Produces a plain gradient-background "R?" icon at the sizes the manifest and
apple-touch-icon link references. Only re-run when changing the design — the
PNGs are committed to the repo.

Usage:
    source .venv/bin/activate    # for PIL
    python make_icons.py
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent.resolve()
OUT = HERE.parent / "icons"
OUT.mkdir(parents=True, exist_ok=True)


def make_icon(size, path):
    img = Image.new("RGB", (size, size), "#1e1e2e")
    pix = img.load()
    # Simple diagonal gradient from purple (top-left) to pink (bottom-right)
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            r = int(0x6a + (0xd6 - 0x6a) * t)
            g = int(0x5f + (0x5f - 0x5f) * t)
            b = int(0xff + (0xb0 - 0xff) * t)
            pix[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)
    font_path = next(
        (p for p in (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ) if os.path.exists(p)),
        None,
    )
    font_size = int(size * 0.42)
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

    text = "R?"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1]

    draw.text((tx + 2, ty + 3), text, fill=(0, 0, 0, 120), font=font)
    draw.text((tx, ty), text, fill="white", font=font)

    img.save(path, "PNG")
    print(f"  wrote {path.name} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    # iOS home-screen icon (apple-touch-icon) — 180x180 is the required size
    make_icon(180, OUT / "icon-180.png")
    # Standard PWA sizes
    make_icon(192, OUT / "icon-192.png")
    make_icon(512, OUT / "icon-512.png")
    # Favicon
    make_icon(32, OUT / "favicon-32.png")
