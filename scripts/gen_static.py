"""Hand-authored sheets: hero, link pills, selected work, architecture, profile.

These rarely change, so they are not rebuilt in CI. Run locally:
    python scripts/gen_static.py
"""
import os

from art import ART_DIR, ROOT, THEMES, W, delay, esc, sheet, text, width, write_all

# ---------------------------------------------------------------- hero

ROLES = [
    "Building systems that make a real-world impact.",
    "NestJS, .NET and cloud-native architecture.",
    "Multi-tenant platforms, secure integrations, real traffic.",
]
STACK = ["NestJS", "TypeScript", ".NET", "Laravel", "AWS", "Docker", "CI/CD",
         "MongoDB", "PostgreSQL", "Redis", "OAuth2", "JWT"]


def crop_marks(t, w, h, m=16, s=10):
    d = "".join(
        f"M{x} {y + dy * s}V{y}H{x + dx * s}"
        for x, y, dx, dy in [(m, m, 1, 1), (w - m, m, -1, 1),
                             (m, h - m, 1, -1), (w - m, h - m, -1, -1)])
    return f'<path d="{d}" fill="none" stroke="{t["sage"]}" stroke-width="1"/>'


def hero(t):
    H = 392
    pad = 44
    name = "LEONARDO VANNI"
    size = 96
    size *= (W - 2 * pad) / width("display", name, size, -0.035)

    phrases = []
    for i, p in enumerate(ROLES):
        phrases.append(
            f'<g class="ph{" ov" if i else ""}" style="{delay(i * 4)}">'
            f'{text("serif-i", p, pad, 256, 40, t["fg"])}</g>')

    sep = "   /   "
    unit = sep.join(STACK).upper() + sep
    unit_w = width("mono", unit, 12, 0.08)
    row = "".join(
        text("mono", unit, pad + k * unit_w, 354, 12, t["muted"], track=0.08)
        for k in range(3))

    css = (
        "@keyframes rise{from{opacity:0;transform:translateY(18px)}}"
        "@keyframes ph{0%{opacity:0;transform:translateY(12px)}"
        "5%{opacity:1;transform:none}28%{opacity:1;transform:none}"
        "33.3%{opacity:0;transform:translateY(-12px)}100%{opacity:0}}"
        "@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}"
        "50%{opacity:.35;transform:scale(1.7)}}"
        f"@keyframes mq{{to{{transform:translateX({-unit_w:.1f}px)}}}}"
        ".rise{animation:rise .9s cubic-bezier(.22,1,.36,1) both}"
        ".ph{animation:ph 12s infinite both}"
        ".dot{animation:pulse 2.4s ease-in-out infinite;"
        "transform-box:fill-box;transform-origin:center}"
        ".mq{animation:mq 38s linear infinite}")

    body = (
        crop_marks(t, W, H)
        + text("mono", "LV — PORTFOLIO / 2026", pad, 50, 11, t["muted"], track=0.14)
        + f'<circle class="dot" cx="{W - pad - 118}" cy="46.5" r="3.5" fill="{t["sage"]}"/>'
        + text("mono", "CREATING LUCK", W - pad, 50, 11, t["muted"], "end", 0.14)
        + f'<line x1="{pad}" x2="{W - pad}" y1="68" y2="68" stroke="{t["line"]}"/>'
        + f'<g class="rise" style="{delay(0.1)}">'
        + text("display", name, pad, 168, size, t["fg"], track=-0.035) + "</g>"
        + f'<g class="rise" style="{delay(0.35)}">'
        + text("mono", "BACKEND SOFTWARE ENGINEER  ·  EPICORA", pad, 200, 12, t["deep"], track=0.12)
        + "</g>"
        + f'<g class="rise" style="{delay(0.55)}">{"".join(phrases)}</g>'
        + f'<g class="rise" style="{delay(0.75)}">'
        + text("mono", "Chapecó, SC — Brazil  ·  4+ years  ·  30+ systems shipped",
               pad, 296, 12, t["muted"], track=0.02) + "</g>"
        + f'<line x1="{pad}" x2="{W - pad}" y1="320" y2="320" stroke="{t["line"]}"/>'
        + f'<g clip-path="url(#mqc)"><g class="mq" style="{delay(0)}">{row}</g></g>'
        + f'<defs><linearGradient id="fl"><stop offset="0" stop-color="{t["bg"]}"/><stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>'
        + f'<linearGradient id="fr"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="0"/><stop offset="1" stop-color="{t["bg"]}"/></linearGradient></defs>'
        + f'<rect x="{pad}" y="330" width="60" height="36" fill="url(#fl)"/>'
        + f'<rect x="{W - pad - 60}" y="330" width="60" height="36" fill="url(#fr)"/>'
        + f'<clipPath id="mqc"><rect x="{pad}" y="330" width="{W - 2 * pad}" height="36"/></clipPath>'
    )
    return sheet(W, H, body, t, css,
                 "Leonardo Vanni — Backend Software Engineer")


# ---------------------------------------------------------------- pills

LINKS = [
    ("portfolio", "PORTFOLIO", True),
    ("linkedin", "LINKEDIN", False),
    ("instagram", "INSTAGRAM", False),
]


def pill(label, primary):
    def build(t):
        tw = width("mono-b", label, 12, 0.14)
        w, h = int(tw + 62), 40
        fg, bg = (t["bg"], t["fg"]) if primary else (t["fg"], t["bg"])
        ax, ay = w - 28, 20
        arrow = (f'<path d="M{ax} {ay + 5}L{ax + 10} {ay - 5}M{ax + 2} {ay - 5}H{ax + 10}V{ay + 3}" '
                 f'fill="none" stroke="{fg}" stroke-width="1.5" stroke-linecap="round" '
                 f'stroke-linejoin="round"/>')
        body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" '
                f'fill="{bg if primary else "none"}" stroke="{t["fg"]}" '
                f'stroke-opacity="{1 if primary else .35}"/>'
                + text("mono-b", label, 22, 24.5, 12, fg, track=0.14) + arrow)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}" role="img" aria-label="{label.title()}">{body}</svg>')
    return build


# ---------------------------------------------------------------- work

CASES = [
    ("01", "1.5k+", "USERS", "Sports Consulting SaaS",
     "White-label tenants with strict data isolation and a contextual AI chat.",
     ["NestJS", "Multi-tenant", "MongoDB", "Redis"], "45k+ workouts · 24k+ diet records"),
    ("02", "61k+", "PROPOSALS", "Vehicle Financing Management",
     "Real-time ERP and inventory sync, validated across financial institutions.",
     ["NestJS", "ERP", "Security", "MongoDB"], "13k+ financings · 135+ daily users"),
    ("03", "20 GB", "UPLOADS", "Video & Marketing Production",
     "AI agents, Stripe subscriptions and two-way Google Calendar sync.",
     ["NestJS", "Microservices", "Stripe", "Google API"], "100+ large files, in real time"),
]


def wrap(font, s, size, maxw):
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and width(font, trial, size) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def work(t):
    H, pad, gap = 412, 44, 18
    cw = (W - 2 * pad - 2 * gap) / 3
    css = ("@keyframes rise{from{opacity:0;transform:translateY(16px)}}"
           ".c{animation:rise .8s cubic-bezier(.22,1,.36,1) both}")
    cards = []
    for i, (idx, big, unit, title, desc, tags, foot) in enumerate(CASES):
        x = pad + i * (cw + gap)
        ix = x + 20
        dl = wrap("serif", desc, 17, cw - 40)
        tagrow, tx = [], ix
        for tg in tags:
            tw = width("mono", tg.upper(), 9, 0.08) + 14
            if tx + tw > x + cw - 14:
                break
            tagrow.append(
                f'<rect x="{tx:.1f}" y="322" width="{tw:.1f}" height="20" rx="10" '
                f'fill="none" stroke="{t["line"]}"/>'
                + text("mono", tg.upper(), tx + 7, 335.5, 9, t["muted"], track=0.08))
            tx += tw + 5
        cards.append(
            f'<g class="c" style="{delay(0.1 + i * 0.12)}">'
            f'<rect x="{x:.1f}" y="88" width="{cw:.1f}" height="296" rx="10" '
            f'fill="{t["soft"]}" stroke="{t["line"]}"/>'
            + text("mono", f"({idx})", ix, 116, 11, t["sage"], track=0.1)
            + text("serif", big, ix, 176, 62, t["fg"])
            + text("mono-b", unit, ix, 198, 10, t["deep"], track=0.16)
            + f'<line x1="{ix}" x2="{x + cw - 20:.1f}" y1="214" y2="214" stroke="{t["line"]}"/>'
            + text("display", title, ix, 238, 15, t["fg"], track=-0.01)
            + "".join(text("serif", l, ix, 260 + k * 19, 16, t["muted"])
                      for k, l in enumerate(dl))
            + "".join(tagrow)
            + text("mono", foot.upper(), ix, 370, 8.5, t["muted"], track=0.04)
            + "</g>")
    body = (
        text("mono", "SELECTED WORK / 03", pad, 50, 11, t["muted"], track=0.14)
        + text("mono", "PRODUCTION SYSTEMS", W - pad, 50, 11, t["muted"], "end", 0.14)
        + f'<line x1="{pad}" x2="{W - pad}" y1="68" y2="68" stroke="{t["line"]}"/>'
        + "".join(cards))
    return sheet(W, H, body, t, css, "Selected work: three production systems")


# ---------------------------------------------------------------- architecture

NODES = [("Client", "HTTP / REST"), ("API", "NestJS · Node"),
         ("Cache", "Redis"), ("Database", "MongoDB")]
LINKS_LBL = ["request", "cache check", "query"]


def architecture(t):
    H, pad, bw, bh, cy = 248, 44, 128, 76, 130
    n = len(NODES)
    step = (W - 2 * pad - bw) / (n - 1)
    cx = [pad + bw / 2 + i * step for i in range(n)]
    dur = 9
    arrive = [0, 22, 48, 74]

    kf = ["@keyframes rise{from{opacity:0;transform:translateY(14px)}}",
          "@keyframes flow{to{stroke-dashoffset:-14}}"]
    for i, a in enumerate(arrive):
        kf.append(f"@keyframes n{i}{{0%{{opacity:0}}{max(a - 1, 0)}%{{opacity:0}}"
                  f"{a + 2}%{{opacity:1}}{a + 12}%{{opacity:1}}{a + 17}%{{opacity:0}}100%{{opacity:0}}}}")
    d = step
    kf.append(f"@keyframes fwd{{0%,8%{{transform:translateX(0);opacity:1}}"
              f"22%,34%{{transform:translateX({d:.1f}px);opacity:1}}"
              f"48%,60%{{transform:translateX({2 * d:.1f}px);opacity:1}}"
              f"74%,84%{{transform:translateX({3 * d:.1f}px);opacity:1}}"
              f"86%,100%{{transform:translateX({3 * d:.1f}px);opacity:0}}}}")
    kf.append(f"@keyframes ret{{0%,85%{{transform:translateX({3 * d:.1f}px);opacity:0}}"
              f"86%{{transform:translateX({3 * d:.1f}px);opacity:1}}"
              f"98%{{transform:translateX(0);opacity:1}}100%{{transform:translateX(0);opacity:0}}}}")
    css = "".join(kf) + (
        ".r{animation:rise .8s cubic-bezier(.22,1,.36,1) both}"
        ".fl{animation:flow 1s linear infinite}"
        f".pk{{animation:fwd {dur}s cubic-bezier(.65,0,.35,1) infinite}}"
        f".rt{{animation:ret {dur}s cubic-bezier(.65,0,.35,1) infinite}}"
        + "".join(f".n{i}{{animation:n{i} {dur}s infinite}}" for i in range(n)))

    parts = [
        text("mono", "REQUEST FLOW / LIVE", pad, 50, 11, t["muted"], track=0.14),
        text("mono", "A REQUEST, END TO END", W - pad, 50, 11, t["muted"], "end", 0.14),
        f'<line x1="{pad}" x2="{W - pad}" y1="68" y2="68" stroke="{t["line"]}"/>',
    ]
    for i in range(n - 1):
        x1, x2 = cx[i] + bw / 2, cx[i + 1] - bw / 2
        parts.append(
            f'<line class="fl" style="{delay(0)}" x1="{x1:.1f}" x2="{x2:.1f}" y1="{cy}" y2="{cy}" '
            f'stroke="{t["sage"]}" stroke-width="1.5" stroke-dasharray="4 3"/>'
            + text("mono", LINKS_LBL[i].upper(), (x1 + x2) / 2, cy - 14, 8.5,
                   t["muted"], "middle", 0.12))
    ret_y = cy + bh / 2 + 30
    parts.append(
        f'<path d="M{cx[-1]:.1f} {cy + bh / 2}V{ret_y}H{cx[0]:.1f}V{cy + bh / 2}" fill="none" '
        f'stroke="{t["line"]}" stroke-width="1.2" stroke-dasharray="2 4"/>'
        + text("mono", "RESPONSE", W / 2, ret_y + 18, 8.5, t["muted"], "middle", 0.12))
    for i, (title, sub) in enumerate(NODES):
        x = cx[i] - bw / 2
        parts.append(
            f'<g class="r" style="{delay(0.1 + i * 0.1)}">'
            f'<rect x="{x:.1f}" y="{cy - bh / 2}" width="{bw}" height="{bh}" rx="8" '
            f'fill="{t["soft"]}" stroke="{t["line"]}"/>'
            + text("display", title, cx[i], cy - 4, 17, t["fg"], "middle", -0.01)
            + text("mono", sub.upper(), cx[i], cy + 18, 9, t["muted"], "middle", 0.1)
            + f'<g class="n{i} ov" style="{delay(0)}"><rect x="{x:.1f}" y="{cy - bh / 2}" width="{bw}" height="{bh}" '
            f'rx="8" fill="{t["fg"]}"/>'
            + text("display", title, cx[i], cy - 4, 17, t["bg"], "middle", -0.01)
            + text("mono", sub.upper(), cx[i], cy + 18, 9, t["bg"], "middle", 0.1)
            + "</g></g>")
    for cls, y in (("pk", cy), ("rt ov", ret_y)):
        parts.append(
            f'<g class="{cls}" style="{delay(0)}"><circle cx="{cx[0]:.1f}" cy="{y}" r="11" fill="{t["rust"]}" '
            f'opacity=".22"/><circle cx="{cx[0]:.1f}" cy="{y}" r="5" fill="{t["rust"]}"/></g>')
    return sheet(W, H, "".join(parts), t, css,
                 "Backend request flow: Client, API, Cache, Database")


# ---------------------------------------------------------------- profile

FIELDS = [
    ("role", "Backend Software Engineer"),
    ("company", "Epicora Software House"),
    ("location", "Chapecó, SC — Brazil"),
    ("experience", "4+ years · 30+ systems shipped"),
    ("languages", "TypeScript · Node.js · C#"),
    ("frameworks", "NestJS · .NET · Laravel"),
    ("cloud", "AWS · Docker · CI/CD"),
    ("data & auth", "MongoDB · PostgreSQL · Redis · OAuth2"),
    ("spoken", "PT native · EN advanced"),
    ("focus", "Scalable backend systems"),
]


def profile(t):
    pad, top = 44, 96
    lines = open(os.path.join(ROOT, "data", "portrait.txt"), encoding="utf-8").read().split("\n")
    ramp = "@%#*+=-:. "
    # Dense glyphs must trace the figure, so the source ramp is flipped.
    lines = ["".join(ramp[len(ramp) - 1 - ramp.index(c)] if c in ramp else c for c in l)
             for l in lines]
    cols = max(map(len, lines))
    adv, lh, fs = 4.15, 6.9, 6.9
    pw = cols * adv
    ph = len(lines) * lh
    H = int(top + ph + 52)
    css = ("@keyframes wipe{from{opacity:0;clip-path:inset(0 100% 0 0)}"
           "to{opacity:1;clip-path:inset(0 0 0 0)}}"
           "@keyframes rise{from{opacity:0;transform:translateY(12px)}}"
           f"@keyframes scan{{0%{{transform:translateY(-30px)}}65%,100%{{transform:translateY({ph:.0f}px)}}}}"
           "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
           ".sc{animation:scan 7s ease-in-out infinite}.cr{animation:blink 1.1s steps(1) infinite}"
           ".p{animation:wipe .7s ease-out both}"
           ".f{animation:rise .7s cubic-bezier(.22,1,.36,1) both}"
           ".a{font-family:ui-monospace,SFMono-Regular,Consolas,'DejaVu Sans Mono',monospace;"
           f"font-size:{fs}px;white-space:pre;font-weight:700;fill:{t['fg']}}}")
    art = "".join(
        f'<text class="a p" x="{pad}" y="{top + (i + 1) * lh:.1f}" textLength="{cols * adv:.0f}" '
        f'lengthAdjust="spacing" style="{delay(i * 0.02)}">{esc(l)}</text>'
        for i, l in enumerate(lines))
    rx0 = pad + pw + 44
    rows = []
    rh = (ph - 6) / len(FIELDS)
    for i, (k, v) in enumerate(FIELDS):
        y = top + 14 + i * rh
        rows.append(
            f'<g class="f" style="{delay(0.3 + i * 0.07)}">'
            + text("mono", k.upper(), rx0, y, 9.5, t["sage"], track=0.14)
            + text("serif", v, rx0, y + 23, 23, t["fg"])
            + f'<line x1="{rx0}" x2="{W - pad}" y1="{y + 32:.1f}" y2="{y + 32:.1f}" stroke="{t["line"]}"/></g>')
    body = (
        text("mono", "WHOAMI / SPEC SHEET", pad, 50, 11, t["muted"], track=0.14)
        + text("mono", "LEONARDO VANNI BONAVIGO", W - pad, 50, 11, t["muted"], "end", 0.14)
        + f'<line x1="{pad}" x2="{W - pad}" y1="68" y2="68" stroke="{t["line"]}"/>'
        + art
        + f'<defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["sage"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["sage"]}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{t["sage"]}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="pc"><rect x="{pad}" y="{top}" width="{pw:.0f}" height="{ph:.0f}"/></clipPath></defs>'
        + f'<g clip-path="url(#pc)"><rect class="sc ov" style="{delay(0)}" x="{pad}" y="{top}" '
        f'width="{pw:.0f}" height="30" fill="url(#sg)"/></g>'
        + "".join(rows)
        + f'<rect class="cr ov" style="{delay(0)}" x="{rx0 + width("serif", FIELDS[-1][1], 23) + 8:.1f}" '
        f'y="{top + 14 + (len(FIELDS) - 1) * rh + 6:.1f}" width="10" height="19" fill="{t["deep"]}"/>')
    return sheet(W, H, body, t, css, "Portrait and profile sheet for Leonardo Vanni")


def main():
    write_all("hero", hero)
    for name, label, primary in LINKS:
        write_all(f"pill-{name}", pill(label, primary))
    write_all("work", work)
    write_all("architecture", architecture)
    for tn, t in THEMES.items():
        with open(os.path.join(ART_DIR, f"profile-{tn}.svg"), "w", encoding="utf-8") as f:
            f.write(profile(t))
    print("wrote art/profile-{light,dark}.svg")


if __name__ == "__main__":
    main()
