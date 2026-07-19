"""Generate self-hosted GitHub stats + top-languages cards as SVG.

Fetches real data from the GitHub GraphQL API (no third-party image service to
rate-limit or pause on us) and renders two theme-matched SVGs:
    stats-card.svg   — key profile numbers
    langs-card.svg   — compact top-languages bar + legend

Auth: reads a token from env GITHUB_TOKEN or GH_TOKEN.
Local run:  GITHUB_TOKEN=$(gh auth token) python scripts/make_github_cards.py
"""
import json
import os
from collections import defaultdict

import requests

from config import ACCENT, BG, DIM, FG, USERNAME

HERE = os.path.dirname(__file__)
STATS_OUT = os.path.join(HERE, "..", "stats-card.svg")
LANGS_OUT = os.path.join(HERE, "..", "langs-card.svg")
CONTRIB_JSON = os.path.join(HERE, "..", "data", "contributions.json")

QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){
          edges{ size node{ name color } }
        }
      }
    }
    contributionsCollection{
      contributionCalendar{ totalContributions }
      totalPullRequestContributions
    }
  }
}
"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN (e.g. GITHUB_TOKEN=$(gh auth token)).")
    resp = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"bearer {token}"},
        json={"query": QUERY, "variables": {"login": USERNAME}},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def summarize(user):
    repos = user["repositories"]["nodes"]
    langs, colors = defaultdict(int), {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or DIM
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:8]

    # Prefer the scraped calendar total (same source as the heatmap, and it
    # includes private contributions); fall back to the GraphQL count.
    contributions = user["contributionsCollection"]["contributionCalendar"][
        "totalContributions"]
    try:
        with open(CONTRIB_JSON, encoding="utf-8") as f:
            contributions = json.load(f).get("total", contributions)
    except FileNotFoundError:
        pass

    return {
        "contributions": contributions,
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "langs": [(n, 100 * s / total, colors[n]) for n, s in top],
    }


def _fmt(n):
    return f"{n:,}"


def render_stats(s) -> str:
    W, H = 440, 200
    tiles = [
        ("Contributions (1y)", _fmt(s["contributions"])),
        ("Repositories", _fmt(s["repos"])),
        ("Followers", _fmt(s["followers"])),
        ("Stars earned", _fmt(s["stars"])),
    ]
    cols, cw, ch = 2, (W - 48) / 2, 58
    ox, oy = 24, 64
    cells = []
    for i, (label, value) in enumerate(tiles):
        cx = ox + (i % cols) * (cw + 8)
        cy = oy + (i // cols) * (ch + 12)
        cells.append(
            f'<g>'
            f'<text x="{cx:.0f}" y="{cy + 26:.0f}" class="num">{value}</text>'
            f'<text x="{cx:.0f}" y="{cy + 46:.0f}" class="lbl">{label}</text>'
            f'</g>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats">
  <style>
    text{{font-family:ui-monospace,'DejaVu Sans Mono',Consolas,monospace;}}
    .title{{fill:{ACCENT};font-size:14px;font-weight:700;}}
    .num{{fill:{FG};font-size:26px;font-weight:700;}}
    .lbl{{fill:{DIM};font-size:12px;}}
    .cell{{opacity:0;animation:fin .5s ease-out forwards;}}
    @keyframes fin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#21262d"/>
  <text x="24" y="36" class="title">~ $ gh stats</text>
  {''.join(f'<g class="cell" style="animation-delay:{i*0.1:.1f}s">{c[len("<g>"):]}' for i, c in enumerate(cells))}
</svg>'''


def render_langs(s) -> str:
    W = 440
    pad = 24
    bar_y = 58
    bar_h = 14
    bar_w = W - pad * 2
    langs = s["langs"]

    segs, x = [], pad
    for name, pct, color in langs:
        w = bar_w * pct / 100.0
        segs.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{max(w,0.5):.1f}" '
                    f'height="{bar_h}" fill="{color}"/>')
        x += w

    rows = (len(langs) + 1) // 2
    leg_y0 = bar_y + bar_h + 28
    line_h = 24
    col_w = bar_w / 2
    legend = []
    for i, (name, pct, color) in enumerate(langs):
        lx = pad + (i % 2) * col_w
        ly = leg_y0 + (i // 2) * line_h
        legend.append(
            f'<circle cx="{lx+5:.0f}" cy="{ly-4:.0f}" r="5" fill="{color}"/>'
            f'<text x="{lx+18:.0f}" y="{ly:.0f}" class="lname">{name}</text>'
            f'<text x="{lx+col_w-16:.0f}" y="{ly:.0f}" class="lpct" '
            f'text-anchor="end">{pct:.1f}%</text>'
        )
    H = leg_y0 + rows * line_h + 6
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}"
     viewBox="0 0 {W} {H:.0f}" role="img" aria-label="Top languages">
  <style>
    text{{font-family:ui-monospace,'DejaVu Sans Mono',Consolas,monospace;}}
    .title{{fill:{ACCENT};font-size:14px;font-weight:700;}}
    .lname{{fill:{FG};font-size:12px;}}
    .lpct{{fill:{DIM};font-size:12px;}}
  </style>
  <rect width="{W}" height="{H:.0f}" rx="12" fill="{BG}"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2:.0f}" rx="12" fill="none" stroke="#21262d"/>
  <text x="24" y="36" class="title">~ $ top --languages</text>
  <clipPath id="barclip"><rect x="{pad}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="7"/></clipPath>
  <g clip-path="url(#barclip)">{''.join(segs)}</g>
  {''.join(legend)}
</svg>'''


def main():
    s = summarize(fetch())
    with open(STATS_OUT, "w", encoding="utf-8") as f:
        f.write(render_stats(s))
    with open(LANGS_OUT, "w", encoding="utf-8") as f:
        f.write(render_langs(s))
    print(f"Wrote {STATS_OUT} and {LANGS_OUT}")
    print(f"  contributions={s['contributions']} repos={s['repos']} "
          f"stars={s['stars']} followers={s['followers']}")


if __name__ == "__main__":
    main()
