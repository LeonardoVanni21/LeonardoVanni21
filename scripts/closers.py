"""Closing sheets built from the contribution calendar alone.

Only daily counts are used, so private work shows up as numbers and nothing
else: no repository names, no commit messages.
"""
import datetime as dt

from art import (PAD, PULSE_CSS, W, delay, head, sheet, text, width)
from stats import MONTHS, WEEKDAYS, grid, parse, short, streaks


# ---------------------------------------------------------------- skyline

def _rng(seed):
    """Tiny deterministic generator so the city never reshuffles between runs."""
    state = [seed * 2654435761 % 4294967296 or 1]

    def nxt():
        state[0] = (state[0] * 1664525 + 1013904223) % 4294967296
        return state[0] / 4294967296
    return nxt


SKY = {
    "dark": dict(top="#111210", bot="#1b241a", back="#141712", front="#1e211c", edge="#323a2d",
                 win="#efdfa6", river="#0e100d", glow="#c9d8b4"),
    "light": dict(top="#e8e7df", bot="#f4f2e8", back="#cdd0c3", front="#8c9a86", edge="#74846f",
                  win="#f2f1e8", river="#d9dacf", glow="#e0b45a"),
}


def _cls(name):
    return f'class="{name}" ' if name else ""


def skyline(contrib):
    cells, weeks = grid(contrib["days"])
    totals, starts = [], []
    for wk in range(weeks):
        days = [(d, di["count"]) for w, wd, d, di in cells if w == wk]
        totals.append(sum(c for _, c in days))
        starts.append(min(d for d, _ in days))
    peak = max(totals)
    peak_i = totals.index(peak)
    months = {}
    for d, c, _ in parse(contrib["days"]):
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    m_peak = max(months.values())
    bands = []  # [month key, first week, one past last week]
    for i in range(weeks):
        key = (starts[i].year, starts[i].month)
        if bands and bands[-1][0] == key:
            bands[-1][2] = i + 1
        else:
            bands.append([key, i, i + 1])

    H, ground = 496, 412
    pitch = (W - 2 * PAD + 2.5) / weeks
    bw = pitch - 2.5
    max_h = 226

    def build(t):
        k = SKY[t["mode"]]
        dark = t["mode"] == "dark"
        css = (
            "@keyframes grow{from{transform:scaleY(0)}}"
            "@keyframes tw{0%,100%{opacity:1}50%{opacity:.25}}"
            "@keyframes tw2{0%,100%{opacity:.15}40%{opacity:1}}"
            "@keyframes blink{0%,60%,100%{opacity:.15}30%{opacity:1}}"
            "@keyframes drift{from{transform:translateX(-160px)}to{transform:translateX(1020px)}}"
            "@keyframes fly{0%{transform:translateX(-80px)}55%,100%{transform:translateX(960px)}}"
            "@keyframes breathe{0%,100%{opacity:.55}50%{opacity:1}}"
            "@keyframes rise{from{opacity:0;transform:translateY(10px)}}"
            ".bd{animation:grow 1.3s cubic-bezier(.22,1,.36,1) both;"
            "transform-box:fill-box;transform-origin:bottom}"
            ".t1{animation:tw 4.7s ease-in-out infinite both}"
            ".t2{animation:tw2 6.3s ease-in-out infinite both}"
            ".bl{animation:blink 1.8s ease-in-out infinite both}"
            ".cd{animation:drift 90s linear infinite both}"
            ".pl{animation:fly 34s linear infinite both}"
            ".br{animation:breathe 6s ease-in-out infinite both}"
            ".lb{animation:rise .9s cubic-bezier(.22,1,.36,1) 1.4s both}")
        P = [head(t, "SKYLINE / LAST 12 MONTHS", "ONE BUILDING PER WEEK", live=True)]
        win_op = ".10" if dark else ".22"
        P.append(
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{k["top"]}"/><stop offset="1" stop-color="{k["bot"]}"/>'
            f'</linearGradient>'
            f'<linearGradient id="fadeR" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{k["river"]}" stop-opacity=".25"/>'
            f'<stop offset="1" stop-color="{k["river"]}" stop-opacity="1"/></linearGradient>'
            f'<radialGradient id="halo"><stop offset="0" stop-color="{k["glow"]}" stop-opacity=".5"/>'
            f'<stop offset="1" stop-color="{k["glow"]}" stop-opacity="0"/></radialGradient>'
            f'<pattern id="wp" width="5" height="6" patternUnits="userSpaceOnUse">'
            f'<rect x="1" y="1.4" width="2.4" height="3" fill="{k["win"]}" opacity="{win_op}"/>'
            f'</pattern>'
            f'<clipPath id="skyc"><rect x="1" y="69" width="{W - 2}" height="{ground - 69}"/></clipPath>'
            f'<clipPath id="rvc"><rect x="1" y="{ground}" width="{W - 2}" height="{H - ground - 1}"/></clipPath>'
            f'<clipPath id="shc"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14"/></clipPath></defs>'
            f'<rect x="1" y="69" width="{W - 2}" height="{ground - 69}" fill="url(#sky)"/>')

        rnd = _rng(7)
        sky_items = []
        for j, (key, i0, i1) in enumerate(bands):
            if j % 2 == 0:
                bx = PAD + i0 * pitch - 1.25
                sky_items.append(
                    f'<rect x="{bx:.1f}" y="69" width="{(i1 - i0) * pitch:.1f}" height="{ground - 69}" '
                    f'fill="{t["fg"]}" opacity="{.028 if dark else .035}"/>')
        if dark:
            for i in range(46):
                x, y = PAD + rnd() * (W - 2 * PAD), 80 + rnd() * 150
                r = 0.5 + rnd() * 0.9
                sky_items.append(
                    f'<circle {_cls(("t1", "t2", "")[i % 3])}style="{delay(rnd() * 5)}" cx="{x:.1f}" '
                    f'cy="{y:.1f}" r="{r:.1f}" fill="{t["fg"]}" opacity="{.55 + rnd() * .4:.2f}"/>')
            sky_items.append(
                f'<circle cx="150" cy="122" r="46" fill="url(#halo)" class="br" style="{delay(0)}"/>'
                f'<mask id="mn"><rect x="100" y="80" width="100" height="90" fill="#fff"/>'
                f'<circle cx="159" cy="115" r="15" fill="#000"/></mask>'
                f'<circle cx="150" cy="122" r="17" fill="#ecebe0" mask="url(#mn)"/>')
        else:
            sky_items.append(
                f'<circle cx="150" cy="124" r="64" fill="url(#halo)" class="br" style="{delay(0)}"/>'
                f'<circle cx="150" cy="124" r="19" fill="{k["glow"]}"/>')
        cloud_fill = t["fg"] if dark else "#ffffff"
        for cy_, sc, spd in ((104, 1.0, 0), (150, 0.7, -30), (86, 0.55, -58)):
            sky_items.append(
                f'<g class="cd" style="{delay(spd)}" opacity="{.07 if dark else .55}">'
                f'<g transform="translate(0 {cy_}) scale({sc})" fill="{cloud_fill}">'
                f'<ellipse cx="0" cy="0" rx="46" ry="11"/><ellipse cx="22" cy="-8" rx="26" ry="11"/>'
                f'<ellipse cx="-20" cy="-6" rx="22" ry="9"/></g></g>')
        sky_items.append(
            f'<g class="pl" style="{delay(0)}"><g transform="translate(0 96)">'
            f'<path d="M0 0h14l-3 -3h-3l-1 3zM5 0l-5 5h3l5 -5z" fill="{t["fg"]}" opacity=".75"/>'
            f'<circle class="bl" style="{delay(0)}" cx="-1" cy="0" r="1.8" fill="{t["rust"]}"/></g></g>')
        for g in (50, 100, 150, 200):
            gy = ground - 14 - (max_h - 14) * g / peak
            sky_items.append(
                f'<line x1="{PAD}" x2="{W - PAD}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="{t["fg"]}" '
                f'stroke-opacity=".16" stroke-dasharray="2 5"/>'
                + text("mono", str(g), PAD - 8, gy + 3, 8, t["muted"], "end", 0.1))
        P.append(f'<g clip-path="url(#skyc)">{"".join(sky_items)}</g>')

        # back layer: one wide tower per month
        back = []
        for key, i0, i1 in bands:
            h = 46 + 104 * (months.get(key, 0) / m_peak)
            x = PAD + i0 * pitch + 3
            mw = (i1 - i0) * pitch - 8
            back.append(f'<rect x="{x:.1f}" y="{ground - h:.1f}" width="{mw:.1f}" height="{h:.1f}" '
                        f'fill="{k["back"]}"/>'
                        f'<rect x="{x:.1f}" y="{ground - h:.1f}" width="{mw:.1f}" height="{h:.1f}" '
                        f'fill="url(#wp)"/>')
        city = ["".join(back)]

        # front layer: one building per week
        top_order = sorted(range(weeks), key=lambda i: -totals[i])[:6]
        for i in range(weeks):
            v = totals[i]
            h = 14 + (max_h - 14) * (v / peak)
            x = PAD + i * pitch
            top = ground - h
            r = _rng(starts[i].toordinal())
            frac = 0.25 + 0.6 * (v / peak)
            buckets = {"": [], "t1": [], "t2": []}
            for row in range(int((h - 8) // 6)):
                for col in range(2):
                    if r() < frac:
                        wx, wy = x + 2.4 + col * 4.6, top + 5 + row * 6
                        buckets[("", "", "", "t1", "t2")[int(r() * 5)]].append(
                            f"M{wx:.1f} {wy:.1f}h2.6v3h-2.6z")
            wins = "".join(
                f'<path {_cls(c)}style="{delay(i * 0.41 % 5)}" d="{"".join(d)}" fill="{k["win"]}"/>'
                for c, d in buckets.items() if d)
            extra = ""
            if i in top_order:
                extra = (f'<line x1="{x + bw / 2:.1f}" x2="{x + bw / 2:.1f}" y1="{top:.1f}" '
                         f'y2="{top - 9:.1f}" stroke="{k["edge"]}"/>'
                         f'<circle class="bl" style="{delay(i * 0.53 % 2)}" cx="{x + bw / 2:.1f}" '
                         f'cy="{top - 10:.1f}" r="1.6" fill="{t["rust"]}"/>')
            city.append(
                f'<g class="bd" style="{delay(0.1 + i * 0.03)}">'
                f'<title>Week of {short(starts[i])}: {v} contributions</title>'
                f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{k["front"]}"/>'
                f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="1.4" fill="{k["edge"]}"/>'
                f'{wins}{extra}</g>')
        P.append(f'<g id="city">{"".join(city)}</g>')

        # river with a faded reflection
        P.append(f'<rect x="1" y="{ground}" width="{W - 2}" height="{H - ground - 1}" fill="{k["river"]}"/>')
        P.append(f'<g clip-path="url(#rvc)" opacity="{.34 if dark else .22}">'
                 f'<use href="#city" transform="translate(0 {2 * ground}) scale(1 -1)"/></g>')
        P.append(f'<rect x="1" y="{ground}" width="{W - 2}" height="{H - ground - 1}" fill="url(#fadeR)"/>')
        P.append(f'<line x1="{PAD}" x2="{W - PAD}" y1="{ground}" y2="{ground}" stroke="{t["line"]}"/>')

        ticks = "".join(f"M{PAD + i * pitch + bw / 2:.1f} {ground + 2}v4" for i in range(weeks))
        P.append(f'<path d="{ticks}" stroke="{t["muted"]}" stroke-opacity=".55" stroke-width="1" fill="none"/>')
        labeled = False
        for key, i0, i1 in bands:
            bx0, bx1 = PAD + i0 * pitch - 1.25, PAD + i1 * pitch - 1.25
            P.append(f'<line x1="{bx0:.1f}" x2="{bx0:.1f}" y1="{ground + 8}" y2="{ground + 28}" '
                     f'stroke="{t["line"]}"/>')
            if bx1 - bx0 < 34:
                continue
            name = MONTHS[key[1] - 1].upper()
            if not labeled or key[1] == 1:
                name += f" '{key[0] % 100:02d}"
            labeled = True
            P.append(text("mono", name, (bx0 + bx1) / 2, ground + 22, 8.5, t["deep"], "middle", 0.12))

        # "you are here" pin on the current week, named on the time axis
        li = weeks - 1
        lcx = PAD + li * pitch + bw / 2
        ltop = ground - (14 + (max_h - 14) * totals[li] / peak)
        P.append(
            f'<g class="lb" style="{delay(0.2)}">'
            f'<path d="M{lcx - 4:.1f} {ltop - 10:.1f}h8l-4 6z" fill="{t["rust"]}"/>'
            f'<path d="M{lcx - 3.5:.1f} {ground + 40}h7l-3.5 -6z" fill="{t["rust"]}"/>'
            + text("mono-b", "THIS WEEK", lcx - 9, ground + 40, 8.5, t["fg"], "end", 0.14) + "</g>")

        # flag on the busiest week
        fx = PAD + peak_i * pitch + bw / 2
        ftop = ground - max_h
        lbl = f"BUSIEST WEEK  {short(starts[peak_i]).upper()}  ·  {peak}"
        lw = width("mono-b", lbl, 9.5, 0.12) + 24
        lx = min(fx + 10, W - PAD - lw)
        P.append(
            f'<g class="lb" style="{delay(0)}"><line x1="{fx:.1f}" x2="{fx:.1f}" y1="{ftop - 10:.1f}" '
            f'y2="{ftop - 34:.1f}" stroke="{t["rust"]}" stroke-width="1.4"/>'
            f'<path d="M{fx:.1f} {ftop - 34:.1f}h12l-3 5l3 5h-12z" fill="{t["rust"]}"/>'
            f'<rect x="{lx - 8:.1f}" y="{ftop - 62:.1f}" width="{lw:.1f}" height="20" rx="10" '
            f'fill="{k["river"] if dark else t["bg"]}" fill-opacity=".85" stroke="{t["line"]}"/>'
            + text("mono-b", lbl, lx + 4, ftop - 48.5, 9.5, t["fg"], track=0.12) + "</g>")
        P.append(text("mono", "1 BUILDING = 1 WEEK  /  HEIGHT = CONTRIBUTIONS  /  LIT WINDOWS = ACTIVITY",
                      PAD, H - 22, 8.5, t["muted"], track=0.12))
        body = "".join(P)
        # Everything between the header and the border is clipped to the rounded sheet.
        i = body.rindex("<rect", 0, body.index('fill="url(#sky)"'))
        body = body[:i] + f'<g clip-path="url(#shc)">{body[i:]}</g>'
        return sheet(W, H, body, t, css, "Skyline of the year: one building per week")
    return build


# ---------------------------------------------------------------- split-flap board

BOARD = dict(panel="#121311", edge="#2b2e28", cell="#1e201c", hair="#0a0b09",
             ink="#ece9de", dim="#aeb2a4", led_on="#7fa070", led_warn="#c9b48a")
LABEL_CELLS, VALUE_CELLS = 12, 12
PERIOD_S = 16.0


def _pad(s, n):
    return s.upper()[:n].ljust(n)


def _pages(contrib):
    rows = parse(contrib["days"])
    s = streaks(contrib["days"])
    mon = lambda d: short(d).split()[0].upper()
    top = max(rows, key=lambda r: r[1])
    months = {}
    for d, c, _ in rows:
        months[(d.year, d.month)] = months.get((d.year, d.month), 0) + c
    bm = max(months, key=months.get)
    avg = sum(r[1] for r in rows) / len(rows)

    by_wd = [0] * 7
    for d, c, _ in rows:
        by_wd[d.weekday()] += c
    weekend_active = sum(1 for d, c, _ in rows if c and d.weekday() >= 5)
    # Sunday-first weeks, the same buckets as the skyline.
    cells, _ = grid(contrib["days"])
    weeks = {}
    for wk, _wd, d, di in cells:
        start, total = weeks.get(wk, (d, 0))
        weeks[wk] = (min(start, d), total + di["count"])
    best_wk = max(weeks, key=lambda k: weeks[k][1])
    bw, bw_total = weeks[best_wk]

    page1 = [
        ("BUSIEST DAY", f"{mon(top[0])} {top[0].day:02d} - {top[1]}"),
        ("BEST MONTH", f"{MONTHS[bm[1] - 1].upper()} - {months[bm]}"),
        ("STREAK", f"{s['cur']} DAYS"),
        ("ACTIVE DAYS", f"{s['active']} / {s['n']}"),
        ("AVG / DAY", f"{avg:.1f}"),
    ]
    page2 = [
        ("LAST 7 DAYS", str(sum(r[1] for r in rows[-7:]))),
        ("LAST 30 DAYS", str(sum(r[1] for r in rows[-30:]))),
        ("BEST WEEKDAY", WEEKDAYS[by_wd.index(max(by_wd))].upper()),
        ("BUSIEST WEEK", f"{mon(bw)} {bw.day:02d} - {bw_total}"),
        ("WEEKEND DAYS", f"{weekend_active} ACTIVE"),
    ]
    return page1, page2, s


def flap(contrib):
    page1, page2, s = _pages(contrib)
    rnd = _rng(11)
    alphabet = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    pad_x, top0, pitch = PAD + 22, 140, 58
    lw, lh, lgap = 15, 28, 2.5
    vw, vh, vgap = 34, 46, 4
    vx0 = pad_x + LABEL_CELLS * (lw + lgap) + 28
    H = 480

    def build(t):
        B = BOARD
        css = PULSE_CSS + (
            "@keyframes f1{0%,46%{transform:scaleY(1)}46.75%,98.25%{transform:scaleY(0)}"
            "99%,100%{transform:scaleY(1)}}"
            "@keyframes f2{0%,48.25%{transform:scaleY(0)}49%,96%{transform:scaleY(1)}"
            "96.75%,100%{transform:scaleY(0)}}"
            "@keyframes fr{0%,46.75%{transform:scaleY(0)}47.5%{transform:scaleY(1)}"
            "48.25%,96.75%{transform:scaleY(0)}97.5%{transform:scaleY(1)}98.25%,100%{transform:scaleY(0)}}"
            "@keyframes p1{0%,46%{opacity:1}49%,96%{opacity:.22}99%,100%{opacity:1}}"
            "@keyframes p2{0%,46%{opacity:.22}49%,96%{opacity:1}99%,100%{opacity:.22}}"
            "@keyframes led{0%,100%{opacity:1}50%{opacity:.25}}"
            "@keyframes rise{from{opacity:0;transform:translateY(12px)}}"
            f".f1{{animation:f1 {PERIOD_S:.0f}s linear infinite both}}"
            f".f2{{animation:f2 {PERIOD_S:.0f}s linear infinite both}}"
            f".fr{{animation:fr {PERIOD_S:.0f}s linear infinite both}}"
            f".p1{{animation:p1 {PERIOD_S:.0f}s linear infinite both}}"
            f".p2{{animation:p2 {PERIOD_S:.0f}s linear infinite both}}"
            ".led{animation:led 1.6s ease-in-out infinite both}"
            ".bd{animation:rise .9s cubic-bezier(.22,1,.36,1) both}")
        P = [head(t, "BOARD / COMMITS", "REAL NUMBERS, ONE PAGE AT A TIME", live=True)]
        ph = top0 - 118 + 5 * pitch + 6
        P.append(
            f'<g class="bd" style="{delay(0.05)}">'
            f'<rect x="{PAD}" y="88" width="{W - 2 * PAD}" height="{ph + 30}" rx="12" '
            f'fill="{B["panel"]}" stroke="{B["edge"]}"/>')
        # board header strip
        healthy = s["cur"] > 0
        led = B["led_on"] if healthy else B["led_warn"]
        P.append(
            text("mono-b", "COMMIT BOARD", pad_x, 119, 11, B["ink"], track=0.2)
            + text("mono", f"FLIGHT LV-{s['cur']}", W - PAD - 130, 119, 9.5, B["dim"], "end", 0.16)
            + f'<circle class="led" style="{delay(0)}" cx="{W - PAD - 112}" cy="115.5" r="3.4" fill="{led}"/>'
            + text("mono-b", "ON TIME" if healthy else "DELAYED", W - PAD - 22, 119, 9.5, led, "end", 0.16)
            + f'<line x1="{pad_x}" x2="{W - PAD - 22}" y1="128" y2="128" stroke="{B["edge"]}"/>')

        def cell(x, y, w, h, c1, c2, size, color, seed, d):
            cx, cy = x + w / 2, y + h / 2
            base = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="3.5" fill="{B["cell"]}"/>')
            by = cy + size * 0.36

            def glyph(ch, cls, extra=""):
                if ch == " ":
                    return ""
                return (f'<g class="{cls}{extra}" style="transform-origin:{cx:.1f}px {cy:.1f}px;'
                        f'{delay(d)}">' + text("mono-b", ch, cx, by, size, color, "middle") + "</g>")

            hinge = (f'<rect x="{x:.1f}" y="{cy - .7:.1f}" width="{w}" height="1.4" fill="{B["hair"]}"/>')
            if c1 == c2:
                return base + (text("mono-b", c1, cx, by, size, color, "middle") if c1 != " " else "") + hinge
            mid = alphabet[int(rnd() * len(alphabet))]
            return (base + glyph(c1, "f1") + glyph(mid, "fr", " ov") + glyph(c2, "f2", " ov") + hinge)

        for r in range(5):
            y = top0 + r * pitch
            (l1, v1), (l2, v2) = page1[r], page2[r]
            l1, l2, v1, v2 = _pad(l1, LABEL_CELLS), _pad(l2, LABEL_CELLS), _pad(v1, VALUE_CELLS), _pad(v2, VALUE_CELLS)
            for i in range(LABEL_CELLS):
                P.append(cell(pad_x + i * (lw + lgap), y + (vh - lh) / 2, lw, lh, l1[i], l2[i], 17,
                              B["dim"], r * 31 + i, r * 0.13 + i * 0.045))
            for i in range(VALUE_CELLS):
                P.append(cell(vx0 + i * (vw + vgap), y, vw, vh, v1[i], v2[i], 31, B["ink"],
                              r * 17 + i, r * 0.13 + i * 0.045 + 0.2))
        P.append("</g>")
        py = 88 + ph + 30 + 22
        P.append(text("mono", "THE BOARD FLIPS BETWEEN RECORDS AND RECENT FORM", PAD, py, 9, t["muted"], track=0.14))
        P.append(f'<circle class="p1" style="{delay(0)}" cx="{W - PAD - 14}" cy="{py - 3.5}" r="3.6" fill="{t["deep"]}"/>'
                 f'<circle class="p2" style="{delay(0)}" cx="{W - PAD - 2}" cy="{py - 3.5}" r="3.6" fill="{t["deep"]}"/>')
        return sheet(W, py + 26, "".join(P), t, css, "Split-flap board with real contribution numbers")
    return build
