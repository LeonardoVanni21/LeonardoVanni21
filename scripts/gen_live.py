"""Data-driven sheets rebuilt daily by CI: activity, numbers, languages.

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

from art import ROOT, USERNAME, W, delay, sheet, text, width, write_all

CONTRIB = os.path.join(ROOT, "data", "contributions.json")
GH_CACHE = os.path.join(ROOT, "data", "github.json")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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


def streaks(days):
    days = sorted(days, key=lambda d: d["date"])
    dates = [dt.date.fromisoformat(d["date"]) for d in days]
    counts = [d["count"] for d in days]
    i = len(days) - 1
    if counts[i] == 0:  # a still-empty "today" must not break the streak
        i -= 1
    cur, cur_end = 0, dates[i] if i >= 0 else None
    while i >= 0 and counts[i] > 0:
        cur, cur_start, i = cur + 1, dates[i], i - 1
    best = run = 0
    best_start = best_end = run_start = None
    for j, c in enumerate(counts):
        if c > 0:
            run += 1
            run_start = dates[j] if run == 1 else run_start
            if run > best:
                best, best_start, best_end = run, run_start, dates[j]
        else:
            run = 0
    return dict(cur=cur, cur_range=(cur_start, cur_end) if cur else None,
                best=best, best_range=(best_start, best_end),
                active=sum(1 for c in counts if c), n=len(counts),
                top=max(counts))


def short(d):
    return f"{MONTHS[d.month - 1]} {d.day}"


def rng(r):
    if not r:
        return "—"
    a, b = r
    return short(a) if a == b else f"{short(a)} – {short(b)}"


def head(t, left, right):
    pad = 44
    return (text("mono", left, pad, 50, 11, t["muted"], track=0.14)
            + text("mono", right, W - pad, 50, 11, t["muted"], "end", 0.14)
            + f'<line x1="{pad}" x2="{W - pad}" y1="68" y2="68" stroke="{t["line"]}"/>')


# ---------------------------------------------------------------- activity

def activity(contrib):
    days = contrib["days"]
    cells, week, prev = [], 0, None
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        wd = (date.weekday() + 1) % 7
        if prev is not None and wd <= prev:
            week += 1
        prev = wd
        cells.append((week, wd, date, d))
    weeks = week + 1
    pad, label_w, pitch, cell = 44, 30, 14.0, 11
    ox, oy = pad + label_w, 168
    step = 1.1 / (weeks + 6)
    updated = days[-1]["date"]
    last = dt.date.fromisoformat(updated)
    H = 330

    def build(t):
        css = ("@keyframes drop{from{opacity:0;transform:translateY(-8px)}}"
               ".c{animation:drop .5s ease-out both}"
               "@keyframes rise{from{opacity:0;transform:translateY(14px)}}"
               ".h{animation:rise .8s cubic-bezier(.22,1,.36,1) both}")
        parts = [head(t, "ACTIVITY / LAST 12 MONTHS", "REFRESHED DAILY BY GITHUB ACTIONS")]
        parts.append(
            f'<g class="h" style="{delay(0.05)}">'
            + text("serif", f'{contrib["total"]:,}', pad, 134, 56, t["fg"])
            + text("mono", "CONTRIBUTIONS IN THE LAST YEAR",
                   pad + width("serif", f'{contrib["total"]:,}', 56) + 16, 132, 11,
                   t["deep"], track=0.14) + "</g>")
        lx = W - pad - 5 * 15 - 78
        leg = text("mono", "LESS", lx, 132, 9, t["muted"], track=0.12)
        for i, c in enumerate(t["heat"]):
            leg += f'<rect x="{lx + 38 + i * 15}" y="123" width="11" height="11" rx="3" fill="{c}"/>'
        leg += text("mono", "MORE", lx + 38 + 5 * 15 + 4, 132, 9, t["muted"], track=0.12)
        parts.append(leg)

        seen = set()
        for wk, wd, date, _ in cells:
            key = (date.year, date.month)
            if wd == 0 and key not in seen and date.day <= 7:
                seen.add(key)
                parts.append(text("mono", MONTHS[date.month - 1].upper(),
                                  ox + wk * pitch, oy - 8, 8.5, t["muted"], track=0.1))
        for wd, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
            parts.append(text("mono", name, pad, oy + wd * pitch + 9, 8, t["muted"], track=0.08))
        for wk, wd, date, d in cells:
            x, y = ox + wk * pitch, oy + wd * pitch
            today = (' stroke="%s" stroke-width="1.4"' % t["rust"]) if date == last else ""
            parts.append(
                f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{t["heat"][min(d["level"], 4)]}"{today} '
                f'style="{delay((wk + wd) * step)}"/>')
        parts.append(text("mono", f"LAST SYNC {short(last).upper()}, {last.year}",
                          pad, H - 24, 9, t["muted"], track=0.14))
        return sheet(W, H, "".join(parts), t, css,
                     f'{contrib["total"]} contributions in the last year')
    return build


# ---------------------------------------------------------------- numbers

def numbers(contrib, gh):
    s = streaks(contrib["days"])
    items = [
        (f'{contrib["total"]:,}', "CONTRIBUTIONS", "last 12 months"),
        (str(s["cur"]), "CURRENT STREAK", rng(s["cur_range"])),
        (str(s["best"]), "LONGEST STREAK", rng(s["best_range"])),
        (f'{s["active"]}', "ACTIVE DAYS", f'busiest day · {s["top"]}'),
        (str(gh["repos"]), "REPOSITORIES", "public, original"),
    ]

    def build(t):
        H, pad = 220, 44
        cw = (W - 2 * pad) / len(items)
        css = ("@keyframes rise{from{opacity:0;transform:translateY(16px)}}"
               ".n{animation:rise .8s cubic-bezier(.22,1,.36,1) both}")
        parts = [head(t, "NUMBERS / LIVE", "SELF-HOSTED · NO THIRD PARTY")]
        for i, (big, label, sub) in enumerate(items):
            x = pad + i * cw + (0 if i == 0 else 18)
            if i:
                parts.append(f'<line x1="{pad + i * cw:.1f}" x2="{pad + i * cw:.1f}" '
                             f'y1="94" y2="186" stroke="{t["line"]}"/>')
            parts.append(
                f'<g class="n" style="{delay(0.1 + i * 0.1)}">'
                + text("serif", big, x, 148, 58, t["rust"] if i == 1 else t["fg"])
                + text("mono-b", label, x, 172, 9, t["deep"], track=0.14)
                + text("mono", sub.upper(), x, 188, 8, t["muted"], track=0.06) + "</g>")
        return sheet(W, H, "".join(parts), t, css, "Key GitHub numbers")
    return build


# ---------------------------------------------------------------- languages

def languages(gh):
    langs = gh["langs"]

    def build(t):
        H, pad, bar_y, bar_h = 236, 44, 96, 14
        bw = W - 2 * pad
        css = ("@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}"
               "@keyframes rise{from{opacity:0;transform:translateY(10px)}}"
               ".b{animation:wipe 1.1s cubic-bezier(.22,1,.36,1) both}"
               ".l{animation:rise .6s cubic-bezier(.22,1,.36,1) both}")
        parts = [head(t, "LANGUAGES / BY CODE SIZE", "ALL PUBLIC REPOSITORIES")]
        segs, x = [], pad
        for i, (name, pct) in enumerate(langs):
            w = bw * pct / sum(p for _, p in langs)
            segs.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w - 2, 1):.1f}" '
                        f'height="{bar_h}" rx="3" fill="{t["langs"][i]}"/>')
            x += w
        parts.append(f'<g class="b" style="{delay(0.1)}">{"".join(segs)}</g>')
        colw = bw / 4
        for i, (name, pct) in enumerate(langs):
            cx = pad + (i % 4) * colw
            cy = 154 + (i // 4) * 44
            parts.append(
                f'<g class="l" style="{delay(0.3 + i * 0.06)}">'
                f'<circle cx="{cx + 4:.1f}" cy="{cy - 4}" r="4" fill="{t["langs"][i]}"/>'
                + text("display", name, cx + 16, cy, 14, t["fg"], track=-0.01)
                + text("mono", f"{pct:.1f}%", cx + 16, cy + 17, 10, t["muted"], track=0.06)
                + "</g>")
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


if __name__ == "__main__":
    main()
