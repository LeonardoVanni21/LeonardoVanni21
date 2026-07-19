"""Generate a self-hosted streak card from data/contributions.json.

Uses the same daily data as the heatmap (which includes private contributions
when the profile setting is on), so the numbers always match the calendar and
never depend on a third-party service. Shows total (last year), current streak
and longest streak, in the shared terminal theme.
"""
import datetime as dt
import json
import os

from config import ACCENT, BG, DIM, FG

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "streak-card.svg")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt(d: dt.date) -> str:
    return f"{MONTHS[d.month - 1]} {d.day}"


def compute(days):
    days = sorted(days, key=lambda d: d["date"])
    dates = [dt.date.fromisoformat(d["date"]) for d in days]
    counts = [d["count"] for d in days]
    n = len(days)
    total = sum(counts)

    # Current streak: consecutive active days ending today (a still-zero "today"
    # doesn't break it — count back from the previous day).
    i = n - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    cur = 0
    cur_end = cur_start = None
    while i >= 0 and counts[i] > 0:
        if cur_end is None:
            cur_end = dates[i]
        cur_start = dates[i]
        cur += 1
        i -= 1

    # Longest streak across the window.
    best = run = 0
    best_start = best_end = run_start = None
    for j in range(n):
        if counts[j] > 0:
            run = run + 1 if run else 1
            if run == 1:
                run_start = dates[j]
            if run > best:
                best, best_start, best_end = run, run_start, dates[j]
        else:
            run = 0

    return {
        "total": total,
        "total_start": dates[0] if dates else None,
        "total_end": dates[-1] if dates else None,
        "cur": cur, "cur_start": cur_start, "cur_end": cur_end,
        "best": best, "best_start": best_start, "best_end": best_end,
    }


def col(cx, big, label, sub, ring=False):
    parts = []
    if ring:
        parts.append(f'<circle cx="{cx}" cy="70" r="40" fill="none" '
                     f'stroke="{ACCENT}" stroke-width="4"/>')
        parts.append(f'<text x="{cx}" y="78" text-anchor="middle" '
                     f'class="big ring">{big}</text>')
    else:
        parts.append(f'<text x="{cx}" y="78" text-anchor="middle" '
                     f'class="big">{big}</text>')
    parts.append(f'<text x="{cx}" y="132" text-anchor="middle" '
                 f'class="lbl">{label}</text>')
    if sub:
        parts.append(f'<text x="{cx}" y="152" text-anchor="middle" '
                     f'class="sub">{sub}</text>')
    return "".join(parts)


def render(s) -> str:
    W, H = 495, 180
    c1, c2, c3 = W / 6, W / 2, 5 * W / 6

    def rng(a, b):
        if not a:
            return ""
        return fmt(a) if a == b else f"{fmt(a)} – {fmt(b)}"

    body = [
        col(c1, f'{s["total"]:,}', "Total (1y)",
            rng(s["total_start"], s["total_end"])),
        col(c2, str(s["cur"]), "Current Streak",
            rng(s["cur_start"], s["cur_end"]), ring=True),
        col(c3, str(s["best"]), "Longest Streak",
            rng(s["best_start"], s["best_end"])),
    ]
    dividers = (
        f'<line x1="{W/3:.0f}" y1="30" x2="{W/3:.0f}" y2="150" stroke="#21262d"/>'
        f'<line x1="{2*W/3:.0f}" y1="30" x2="{2*W/3:.0f}" y2="150" stroke="#21262d"/>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="Contribution streak">
  <style>
    text{{font-family:ui-monospace,'DejaVu Sans Mono',Consolas,monospace;}}
    .big{{fill:{FG};font-size:34px;font-weight:700;}}
    .ring{{fill:{ACCENT};}}
    .lbl{{fill:{ACCENT};font-size:13px;font-weight:700;}}
    .sub{{fill:{DIM};font-size:10px;}}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#21262d"/>
  {dividers}
  {''.join(body)}
</svg>'''


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    s = compute(data["days"])
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(s))
    print(f"Wrote {OUT}")
    print(f"  total={s['total']} current={s['cur']} longest={s['best']}")


if __name__ == "__main__":
    main()
