"""Render data/contributions.json into an animated contrib-heatmap.svg.

The 53-week x 7-day calendar of rounded boxes fills in with a diagonal,
line-after-line slide-down wipe. Animation is pure SVG + inline CSS keyframes,
which GitHub preserves (it strips JS/external CSS but keeps SVG animation).
Each animation plays once and freezes (no loop).
"""
import datetime as dt
import json
import os

from config import BG, DIM, FG, HEATMAP_COLORS

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

CELL = 13          # box size
GAP = 3            # space between boxes
PAD = 20           # outer padding
TOP = 40           # room for header + weekday labels
LABEL_W = 30       # room for weekday labels on the left

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = {1: "Mon", 3: "Wed", 5: "Fri"}


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def layout(days):
    """Assign (week, weekday) grid coordinates. GitHub weeks start on Sunday."""
    cells = []
    week = 0
    prev_wd = None
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        wd = (date.weekday() + 1) % 7  # Mon=0..Sun=6  ->  Sun=0..Sat=6
        if prev_wd is not None and wd <= prev_wd:
            week += 1
        prev_wd = wd
        cells.append({**d, "week": week, "wd": wd, "date_obj": date})
    return cells, week + 1


def month_labels(cells):
    seen = set()
    out = []
    for c in cells:
        key = (c["date_obj"].year, c["date_obj"].month)
        if c["wd"] == 0 and key not in seen and c["date_obj"].day <= 7:
            seen.add(key)
            out.append((c["week"], MONTHS[c["date_obj"].month - 1]))
    return out


def render(data) -> str:
    cells, weeks = layout(data["days"])
    grid_w = weeks * (CELL + GAP)
    grid_h = 7 * (CELL + GAP)
    W = PAD * 2 + LABEL_W + grid_w
    H = PAD + TOP + grid_h + 10
    ox = PAD + LABEL_W
    oy = PAD + TOP

    # Longest diagonal drives the total run time so it always finishes.
    max_diag = weeks + 6
    step = 0.9 / max(max_diag, 1)  # seconds between diagonals

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="ui-monospace,Consolas,monospace" '
        f'role="img" aria-label="{data["total"]} contributions in the last year">',
        "<style>",
        "@keyframes drop{from{opacity:0;transform:translateY(-6px)}"
        "to{opacity:1;transform:translateY(0)}}",
        ".cell{opacity:0;animation:drop .45s ease-out forwards;"
        "transform-box:fill-box}",
        f".hd{{fill:{FG};font-size:13px}}.lbl{{fill:{DIM};font-size:9px}}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="8" fill="{BG}"/>',
        f'<text class="hd" x="{PAD}" y="{PAD + 8}">'
        f'{data["total"]} contributions in the last year</text>',
    ]

    for wk, name in month_labels(cells):
        x = ox + wk * (CELL + GAP)
        parts.append(f'<text class="lbl" x="{x}" y="{oy - 6}">{name}</text>')

    for wd, name in WEEKDAYS.items():
        y = oy + wd * (CELL + GAP) + CELL - 2
        parts.append(f'<text class="lbl" x="{PAD}" y="{y}">{name}</text>')

    for c in cells:
        x = ox + c["week"] * (CELL + GAP)
        y = oy + c["wd"] * (CELL + GAP)
        color = HEATMAP_COLORS[min(c["level"], 4)]
        delay = (c["week"] + c["wd"]) * step
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{color}" style="animation-delay:{delay:.3f}s">'
            f'<title>{c["count"]} on {c["date"]}</title></rect>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    svg = render(load())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
