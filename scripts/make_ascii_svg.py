"""Convert the prepared grayscale portrait into an animated ASCII SVG.

A density ramp maps brightness to characters (sparse for bright areas, dense
for dark). Each row animates with a horizontal clip wipe, staggered top to
bottom. Pure SVG + inline CSS, plays once and freezes.

Usage:
  python scripts/make_ascii_svg.py
"""
import os

import numpy as np
from PIL import Image

from config import ACCENT, BG, FG

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "work", "portrait_gray.png")
OUT = os.path.join(HERE, "..", "leo-ascii.svg")

COLS = 100                # ASCII columns (higher = more facial detail)
CHAR_ASPECT = 0.5         # monospace glyph is ~2x taller than wide
RAMP = "@%#*+=-:. "       # dense (dark) -> sparse (bright)
CH_W = 7                  # px advance per character
CH_H = 12                 # px per row (line height)
PAD = 16


def to_ascii(img: Image.Image):
    w, h = img.size
    rows = max(1, int(COLS * (h / w) * CHAR_ASPECT))
    img = img.resize((COLS, rows))
    arr = np.asarray(img, dtype=np.float32) / 255.0
    n = len(RAMP) - 1
    lines = []
    for row in arr:
        idx = (row * n).round().astype(int)
        lines.append("".join(RAMP[i] for i in idx))
    return lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(lines) -> str:
    cols = max(len(l) for l in lines)
    W = PAD * 2 + cols * CH_W
    H = PAD * 2 + len(lines) * CH_H
    step = min(0.05, 1.2 / max(len(lines), 1))

    rows_svg = []
    for i, line in enumerate(lines):
        y = PAD + (i + 1) * CH_H
        delay = i * step
        rows_svg.append(
            f'<text class="r" x="{PAD}" y="{y}" '
            f'style="animation-delay:{delay:.3f}s">{esc(line)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="ASCII self-portrait">
  <style>
    @keyframes wipe {{
      from {{ clip-path: inset(0 100% 0 0); opacity:0; }}
      to   {{ clip-path: inset(0 0 0 0);    opacity:1; }}
    }}
    text {{
      font-family: ui-monospace, 'DejaVu Sans Mono', Consolas, monospace;
      font-size: 11px; white-space: pre; fill: {FG};
      letter-spacing: 0.5px; dominant-baseline: auto;
    }}
    .r {{ opacity:0; animation: wipe .6s ease-out forwards; }}
  </style>
  <rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10"
        fill="none" stroke="#21262d"/>
  <g>{''.join(rows_svg)}</g>
</svg>'''


def main():
    if not os.path.exists(SRC):
        raise SystemExit(
            f"Missing {SRC}. Run prep_photo.py first.")
    lines = to_ascii(Image.open(SRC).convert("L"))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(lines))
    print(f"Wrote {OUT} ({len(lines)} rows)")


if __name__ == "__main__":
    main()
