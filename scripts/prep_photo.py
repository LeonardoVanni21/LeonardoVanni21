"""Prepare a portrait photo for ASCII conversion (LOCAL step only).

Steps:
  1. Load scripts/input/photo.<ext>
  2. Try to remove the background with rembg (optional — falls back cleanly)
  3. Convert to grayscale, auto-contrast, and composite onto a flat backdrop
  4. Save scripts/work/portrait_gray.png

Usage:
  python scripts/prep_photo.py [path/to/photo.jpg]
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageOps

HERE = os.path.dirname(__file__)
INPUT_DIR = os.path.join(HERE, "input")
WORK_DIR = os.path.join(HERE, "work")
OUT = os.path.join(WORK_DIR, "portrait_gray.png")


def find_input(argv) -> str:
    if len(argv) > 1:
        return argv[1]
    hits = []
    for ext in ("jpg", "jpeg", "png", "webp", "bmp"):
        hits += glob.glob(os.path.join(INPUT_DIR, f"*.{ext}"))
        hits += glob.glob(os.path.join(INPUT_DIR, f"*.{ext.upper()}"))
    if not hits:
        raise SystemExit(
            f"No image found. Put a photo in {INPUT_DIR} or pass a path.")
    return hits[0]


def remove_bg(img: Image.Image) -> Image.Image:
    """Return an RGBA image with background stripped, or None if unavailable."""
    try:
        from rembg import remove
    except Exception as e:  # noqa: BLE001
        print(f"[prep] rembg unavailable ({e}); keeping original background.")
        return None
    try:
        return remove(img).convert("RGBA")
    except Exception as e:  # noqa: BLE001
        print(f"[prep] rembg failed ({e}); keeping original background.")
        return None


def crop_to_portrait(img: Image.Image, ratio: float = 3 / 4) -> Image.Image:
    """Center-crop to a portrait aspect ratio (width/height = ratio)."""
    w, h = img.size
    target_w = min(w, int(h * ratio))
    target_h = min(h, int(target_w / ratio))
    left = (w - target_w) // 2
    top = (h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    path = find_input(sys.argv)
    print(f"[prep] input: {path}")
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)  # honor phone orientation

    cut = remove_bg(img)
    if cut is not None:
        # Composite the cutout over mid-gray so ASCII focuses on the subject.
        bg = Image.new("RGBA", cut.size, (18, 18, 18, 255))
        img = Image.alpha_composite(bg, cut).convert("RGB")

    img = crop_to_portrait(img)
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=2)

    # Gentle gamma lift so mid-tones read as distinct ASCII chars.
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    arr = np.power(arr, 0.85)
    gray = Image.fromarray((arr * 255).astype("uint8"))

    gray.save(OUT)
    print(f"[prep] wrote {OUT} ({gray.size[0]}x{gray.size[1]})")


if __name__ == "__main__":
    main()
