"""Data-driven sheets rebuilt daily by CI: activity, numbers, languages and the closing sheets.

Reads data/contributions.json (scraped by fetch_contributions.py) and the
GitHub GraphQL API. Public profile data only, so the workflow token is enough.
    python scripts/gen_live.py            # fetch + render
    python scripts/gen_live.py --offline  # render from data/github.json
"""
import datetime as dt
import json
import os
import sys
from collections import defaultdict

import requests

from art import (PAD, PULSE_CSS, ROOT, USERNAME, W, delay, head, sheet, text,
                 width, write_all)
from closers import flap, skyline, status
from stats import MONTHS, grid, rng, short, streaks

CONTRIB = os.path.join(ROOT, "data", "contributions.json")
GH_CACHE = os.path.join(ROOT, "data", "github.json")
LABEL_W, PITCH, CELL = 30, 14.0, 11
OX = PAD + LABEL_W

QUERY = """
query($login:String!){
  user(login:$login){
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){
        edges{ size node{ name } } } }
    }
  }
}
"""


# ---------------------------------------------------------------- data

def fetch_github():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (e.g. GITHUB_TOKEN=$(gh auth token)).")
    r = requests.post("https://api.github.com/graphql",
                      headers={"Authorization": f"bearer {token}"},
                      json={"query": QUERY, "variables": {"login": USERNAME}}, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    user = payload["data"]["user"]
    sizes = defaultdict(int)
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            sizes[e["node"]["name"]] += e["size"]
    total = sum(sizes.values()) or 1
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:8]
    data = {"repos": user["repositories"]["totalCount"],
            "langs": [(n, 100 * s / total) for n, s in top]}
    with open(GH_CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    return data


# ---------------------------------------------------------------- activity

def activity(contrib):
    days = contrib["days"]
    cells, weeks = grid(days)
    oy = 168
    step = 1.1 / (weeks + 6)
    last = dt.date.fromisoformat(days[-1]["date"])
    grid_w = weeks * PITCH
    H = 330

    def build(t):
        css = PULSE_CSS + (
            "@keyframes drop{from{opacity:0;transform:translateY(-8px)}}"
            "@keyframes rise{from{opacity:0;transform:translateY(14px)}}"
            f"@keyframes wave{{0%{{transform:translateX(0) skewX(-18deg)}}"
            f"55%,100%{{transform:translateX({grid_w + 180:.0f}px) skewX(-18deg)}}}}"
            "@keyframes tp{0%,100%{stroke-opacity:1}50%{stroke-opacity:.2}}"
            ".c{animation:drop .5s ease-out both}"
            ".h{animation:rise .8s cubic-bezier(.22,1,.36,1) both}"
            ".wv{animation:wave 8s ease-in-out 1.6s infinite;"
            "transform-box:fill-box;transform-origin:center}"
            ".td{animation:tp 1.8s ease-in-out infinite}")
        parts = [head(t, "ACTIVITY / LAST 12 MONTHS", "REFRESHED DAILY BY GITHUB ACTIONS", live=True)]
        parts.append(
            f'<g class="h" style="{delay(0.05)}">'
            + text("serif", f'{contrib["total"]:,}', PAD, 134, 56, t["fg"])
            + text("mono", "CONTRIBUTIONS IN THE LAST YEAR",
                   PAD + width("serif", f'{contrib["total"]:,}', 56) + 16, 132, 11,
                   t["deep"], track=0.14) + "</g>")
        lx = W - PAD - 5 * 15 - 78
        leg = text("mono", "LESS", lx, 132, 9, t["muted"], track=0.12)
        for i, c in enumerate(t["heat"]):
            leg += f'<rect x="{lx + 38 + i * 15}" y="123" width="11" height="11" rx="3" fill="{c}"/>'
        leg += text("mono", "MORE", lx + 38 + 5 * 15 + 4, 132, 9, t["muted"], track=0.12)
        parts.append(leg)

        seen, clip = set(), []
        for wk, wd, date, _ in cells:
            key = (date.year, date.month)
            if wd == 0 and key not in seen and date.day <= 7:
                seen.add(key)
                parts.append(text("mono", MONTHS[date.month - 1].upper(),
                                  OX + wk * PITCH, oy - 8, 8.5, t["muted"], track=0.1))
        for wd, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
            parts.append(text("mono", name, PAD, oy + wd * PITCH + 9, 8, t["muted"], track=0.08))
        for wk, wd, date, d in cells:
            x, y = OX + wk * PITCH, oy + wd * PITCH
            is_today = date == last
            ring = (f' stroke="{t["rust"]}" stroke-width="1.4"' if is_today else "")
            cls = "c td" if is_today else "c"
            parts.append(
                f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{t["heat"][min(d["level"], 4)]}"{ring} '
                f'style="{delay((wk + wd) * step)}"/>')
            clip.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="3"/>')
        parts.append(
            f'<defs><clipPath id="cl">{"".join(clip)}</clipPath>'
            f'<linearGradient id="wg"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{t["glow"]}" stop-opacity="{t["glowop"]}"/>'
            f'<stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></linearGradient></defs>'
            f'<g clip-path="url(#cl)"><rect class="wv ov" style="{delay(0)}" x="{OX - 90}" '
            f'y="{oy - 6}" width="70" height="{7 * PITCH + 8:.0f}" fill="url(#wg)"/></g>')
        parts.append(text("mono", f"LAST SYNC {short(last).upper()}, {last.year}",
                          PAD, H - 24, 9, t["muted"], track=0.14))
        return sheet(W, H, "".join(parts), t, css,
                     f'{contrib["total"]} contributions in the last year')
    return build


# ---------------------------------------------------------------- numbers

def numbers(contrib, gh):
    s = streaks(contrib["days"])
    per_day = contrib["total"] / s["n"]
    items = [
        (f'{contrib["total"]:,}', "CONTRIBUTIONS", "last 12 months", f"avg {per_day:.1f} / day"),
        (str(s["cur"]), "CURRENT STREAK", rng(s["cur_range"]), "days in a row"),
        (str(s["best"]), "LONGEST STREAK", rng(s["best_range"]), "personal record"),
        (f'{s["active"]}', "ACTIVE DAYS", f'busiest day · {s["top"]}',
         f'{100 * s["active"] / s["n"]:.0f}% of the year'),
        (str(gh["repos"]), "REPOSITORIES", "public, original", f'{len(gh["langs"])} languages'),
    ]

    def build(t):
        H = 220
        cw = (W - 2 * PAD) / len(items)
        css = PULSE_CSS + (
            "@keyframes rise{from{opacity:0;transform:translateY(16px)}}"
            "@keyframes sa{0%,42%{opacity:1}50%,92%{opacity:0}100%{opacity:1}}"
            "@keyframes sb{0%,42%{opacity:0}50%,92%{opacity:1}100%{opacity:0}}"
            "@keyframes bar{0%{transform:scaleX(0)}60%,100%{transform:scaleX(1)}}"
            ".n{animation:rise .8s cubic-bezier(.22,1,.36,1) both}"
            ".sa{animation:sa 10s ease-in-out infinite both}"
            ".sb{animation:sb 10s ease-in-out infinite both}"
            ".br{animation:bar 5s cubic-bezier(.65,0,.35,1) infinite;"
            "transform-box:fill-box;transform-origin:left}")
        parts = [head(t, "NUMBERS / LIVE", "SELF-HOSTED · NO THIRD PARTY", live=True)]
        for i, (big, label, sub, alt) in enumerate(items):
            x = PAD + i * cw + (0 if i == 0 else 18)
            if i:
                parts.append(f'<line x1="{PAD + i * cw:.1f}" x2="{PAD + i * cw:.1f}" '
                             f'y1="94" y2="196" stroke="{t["line"]}"/>')
            d = i * 0.9
            parts.append(
                f'<g class="n" style="{delay(0.1 + i * 0.1)}">'
                + text("serif", big, x, 148, 58, t["rust"] if i == 1 else t["fg"])
                + text("mono-b", label, x, 172, 9, t["deep"], track=0.14)
                + f'<g class="sa" style="{delay(d)}">'
                + text("mono", sub.upper(), x, 188, 8, t["muted"], track=0.06) + "</g>"
                + f'<g class="sb ov" style="{delay(d)}">'
                + text("mono", alt.upper(), x, 188, 8, t["sage"], track=0.06) + "</g></g>")
            # Breathing underline: a quiet cue that the sheet is alive.
            parts.append(f'<rect class="br" style="{delay(d)}" x="{x:.1f}" y="196" '
                         f'width="{cw - 40:.1f}" height="1.5" fill="{t["sage"]}" opacity=".7"/>')
        return sheet(W, H, "".join(parts), t, css, "Key GitHub numbers")
    return build


# ---------------------------------------------------------------- languages

def languages(gh):
    langs = gh["langs"]
    n = len(langs)
    slot = 2.2
    cycle = n * slot
    hold = 100 / n - 4

    def build(t):
        H, bar_y, bar_h = 236, 96, 14
        bw = W - 2 * PAD
        css = PULSE_CSS + (
            "@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}"
            "@keyframes rise{from{opacity:0;transform:translateY(10px)}}"
            f"@keyframes spot{{0%,{hold:.1f}%{{opacity:1}}{hold + 4:.1f}%,100%{{opacity:.48}}}}"
            ".b{animation:wipe 1.1s cubic-bezier(.22,1,.36,1) both}"
            ".l{animation:rise .6s cubic-bezier(.22,1,.36,1) both}"
            f".sp{{animation:spot {cycle}s ease-in-out infinite}}")
        parts = [head(t, "LANGUAGES / BY CODE SIZE", "ALL PUBLIC REPOSITORIES", live=True)]
        segs, x = [], PAD
        for i, (name, pct) in enumerate(langs):
            w = bw * pct / sum(p for _, p in langs)
            segs.append(f'<rect class="sp" style="{delay(-(cycle - i * slot))}" x="{x:.1f}" y="{bar_y}" '
                        f'width="{max(w - 2, 1):.1f}" height="{bar_h}" rx="3" fill="{t["langs"][i]}"/>')
            x += w
        parts.append(f'<g class="b" style="{delay(0.1)}">{"".join(segs)}</g>')
        colw = bw / 4
        for i, (name, pct) in enumerate(langs):
            cx = PAD + (i % 4) * colw
            cy = 154 + (i // 4) * 44
            parts.append(
                f'<g class="l" style="{delay(0.3 + i * 0.06)}">'
                f'<g class="sp" style="{delay(-(cycle - i * slot))}">'
                f'<circle cx="{cx + 4:.1f}" cy="{cy - 4}" r="4" fill="{t["langs"][i]}"/>'
                + text("display", name, cx + 16, cy, 14, t["fg"], track=-0.01)
                + text("mono", f"{pct:.1f}%", cx + 16, cy + 17, 10, t["muted"], track=0.06)
                + "</g></g>")
        return sheet(W, H, "".join(parts), t, css, "Top languages by code size")
    return build


def main():
    with open(CONTRIB, encoding="utf-8") as f:
        contrib = json.load(f)
    if "--offline" in sys.argv:
        with open(GH_CACHE, encoding="utf-8") as f:
            gh = json.load(f)
    else:
        gh = fetch_github()
    write_all("activity", activity(contrib))
    write_all("numbers", numbers(contrib, gh))
    write_all("languages", languages(gh))
    write_all("status", status(contrib))
    write_all("skyline", skyline(contrib))
    write_all("flap", flap(contrib))


if __name__ == "__main__":
    main()
