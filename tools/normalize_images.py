#!/usr/bin/env python3
"""
One-shot: normalize every image under ../images/real/ (and optionally ../images/ai/)
to the project standard: max dim 1280 px, JPEG quality 85, progressive, optimized.

Rewrites files in place. Converts non-.jpg files (png/webp) to .jpg and updates
../images.js accordingly.

Usage:
    source .venv/bin/activate
    python normalize_images.py           # real/ only (default)
    python normalize_images.py --all     # real/ and ai/
    python normalize_images.py --dry-run
"""
import argparse
import re
from pathlib import Path

from img_utils import shrink_to_jpeg, OUTPUT_MAX_DIM
from PIL import Image

HERE = Path(__file__).parent.resolve()
REPO = HERE.parent
IMAGES_JS = REPO / "images.js"


def needs_work(path):
    """Return True if this file is oversize *or* has a non-jpg extension."""
    if path.suffix.lower() not in (".jpg", ".jpeg"):
        return True
    try:
        with Image.open(path) as img:
            return max(img.size) > OUTPUT_MAX_DIM
    except Exception:
        return False


def normalize_dir(d, dry_run=False):
    """Returns list of (old_rel_path, new_rel_path) for files whose extension changed."""
    renames = []
    for src in sorted(d.iterdir()):
        if not src.is_file() or src.name.startswith("."):
            continue
        if src.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue

        before_size = src.stat().st_size
        with Image.open(src) as img:
            before_dims = img.size

        action = []
        if max(before_dims) > OUTPUT_MAX_DIM:
            action.append("resize")
        if src.suffix.lower() != ".jpg":
            action.append(f"convert({src.suffix.lower()[1:]}->jpg)")

        if not action:
            continue

        new_name = src.stem + ".jpg"
        new_path = src.with_name(new_name)
        print(f"  {' + '.join(action):<28}  {src.name} ({before_dims[0]}x{before_dims[1]}, {before_size//1024}KB)")

        if dry_run:
            continue

        jpg = shrink_to_jpeg(src.read_bytes())
        new_path.write_bytes(jpg)
        if new_path != src:
            src.unlink()
            renames.append((src.name, new_name))

    return renames


def update_images_js(renames, subdir):
    """Rewrite images/<subdir>/old -> images/<subdir>/new in images.js."""
    if not renames or not IMAGES_JS.exists():
        return
    text = IMAGES_JS.read_text()
    for old, new in renames:
        text = text.replace(f"images/{subdir}/{old}", f"images/{subdir}/{new}")
    IMAGES_JS.write_text(text)
    print(f"  updated images.js ({len(renames)} rename(s) in {subdir}/)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="Also normalize images/ai/")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    dirs = [("real", REPO / "images" / "real")]
    if args.all:
        dirs.append(("ai", REPO / "images" / "ai"))

    for subdir, path in dirs:
        if not path.exists():
            continue
        print(f"\n== {subdir}/ ==")
        renames = normalize_dir(path, dry_run=args.dry_run)
        if not args.dry_run:
            update_images_js(renames, subdir)


if __name__ == "__main__":
    main()
