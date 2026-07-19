"""Render a neofetch-style info card into info-card.svg.

Each line fades and slides in on a short stagger. Pure SVG + inline CSS,
plays once and freezes.
"""
import os

from config import ACCENT, BG, CARD_FIELDS, DIM, FG, FONT, NAME, USERNAME

OUT = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

W = 520
PAD = 24
LINE = 26
KEY_W = 92


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render() -> str:
    title = f"{USERNAME.lower()}@github"
    rule = "-" * len(title)

    rows = []
    y = PAD + 30
    delay = 0.0

    def line(svg_inner: str):
        nonlocal delay
        out = (f'<g class="row" style="animation-delay:{delay:.2f}s">'
               f'{svg_inner}</g>')
        delay += 0.12
        return out

    # Header (user@host) + separator, neofetch style
    rows.append(line(
        f'<text x="{PAD}" y="{y}" class="host">{esc(title)}</text>'))
    y += 18
    rows.append(line(
        f'<text x="{PAD}" y="{y}" class="dim">{esc(rule)}</text>'))
    y += LINE

    # Name line
    rows.append(line(
        f'<text x="{PAD}" y="{y}"><tspan class="key">name</tspan>'
        f'<tspan class="sep">: </tspan>'
        f'<tspan class="val" x="{PAD + KEY_W}">{esc(NAME)}</tspan></text>'))
    y += LINE

    for key, val in CARD_FIELDS:
        rows.append(line(
            f'<text x="{PAD}" y="{y}"><tspan class="key">{esc(key)}</tspan>'
            f'<tspan class="sep">: </tspan>'
            f'<tspan class="val" x="{PAD + KEY_W}">{esc(val)}</tspan></text>'))
        y += LINE

    H = y - LINE + PAD  # tight to the last rendered line

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" font-family="{FONT}" role="img"
     aria-label="Profile info card for {esc(NAME)}">
  <style>
    @keyframes slidein {{
      from {{ opacity:0; transform:translateX(-10px); }}
      to   {{ opacity:1; transform:translateX(0); }}
    }}
    .row {{ opacity:0; animation:slidein .5s ease-out forwards; }}
    text {{ font-size:14px; }}
    .host {{ fill:{ACCENT}; font-size:15px; font-weight:700; }}
    .dim  {{ fill:{DIM}; }}
    .key  {{ fill:{ACCENT}; }}
    .sep  {{ fill:{DIM}; }}
    .val  {{ fill:{FG}; }}
  </style>
  <rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10"
        fill="none" stroke="#21262d"/>
  {''.join(rows)}
</svg>'''


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
