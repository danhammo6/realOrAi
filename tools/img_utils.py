"""Shared image-normalization helpers for the Real or AI? toolchain.

Target profile: max dim 1280 px, JPEG quality 85, progressive, optimized.
Keeps AI and real images indistinguishable by dimensions / filesize.
"""
import io
from PIL import Image

OUTPUT_MAX_DIM = 1280
OUTPUT_JPEG_QUALITY = 85


def shrink_to_jpeg(src_bytes, max_dim=OUTPUT_MAX_DIM, quality=OUTPUT_JPEG_QUALITY):
    """Decode image bytes, downscale so longest side <= max_dim, return JPEG bytes."""
    img = Image.open(io.BytesIO(src_bytes))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dim / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()
