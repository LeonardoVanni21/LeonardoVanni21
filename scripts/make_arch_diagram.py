"""Generate a self-contained animated backend-architecture diagram SVG.

A request 'packet' travels Client -> API -> Cache -> Database, dwelling on
each node (which pulses as it arrives) and looping. Pure SVG + SMIL, no
third-party service. Uses only sanitizer-safe elements (no filters/markers).
"""
import os

from config import ACCENT, BG, DIM, FG

OUT = os.path.join(os.path.dirname(__file__), "..", "architecture.svg")

W, H = 860, 200
CY = 112                       # vertical center of the node row
BW, BH = 150, 74               # box size
DUR = 6.0                      # loop duration (s)

NODES = [
    (95,  "Client", "HTTP / REST"),
    (318, "API", "NestJS · Node"),
    (541, "Cache", "Redis"),
    (764, "Database", "MongoDB"),
]
LINK_LABELS = ["request", "cache check", "query"]

# Packet dwell schedule across the loop (fractions of DUR).
# travel, dwell, travel, dwell, travel, dwell, fast-reset
CX_VALUES = "95;318;318;541;541;764;764;95"
CX_KEYTIMES = "0;0.22;0.30;0.52;0.60;0.82;0.92;1"
ARRIVE = {1: 0.22, 2: 0.52, 3: 0.82, 0: 0.0}  # node index -> arrival fraction


def box(cx, title, sub, idx):
    x = cx - BW / 2
    y = CY - BH / 2
    f = ARRIVE[idx]
    a = max(f - 0.02, 0.0)
    # Glow border that spikes when the packet arrives at this node.
    glow = (
        f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="10" '
        f'fill="none" stroke="{ACCENT}" stroke-width="2" opacity="0">'
        f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
        f'keyTimes="0;{a:.3f};{f:.3f};{min(f + 0.06, 1):.3f};1" '
        f'values="0;0;0.9;0;0"/></rect>'
    )
    return (
        f'<g>'
        f'<rect x="{x}" y="{y}" width="{BW}" height="{BH}" rx="10" '
        f'fill="#0d1117" stroke="#30363d"/>'
        f'{glow}'
        f'<text x="{cx}" y="{CY - 6}" text-anchor="middle" class="ntitle">{title}</text>'
        f'<text x="{cx}" y="{CY + 16}" text-anchor="middle" class="nsub">{sub}</text>'
        f'</g>'
    )


def connector(x1, x2, label):
    mid = (x1 + x2) / 2
    arrow = (f'<polygon points="{x2},{CY} {x2 - 9},{CY - 5} {x2 - 9},{CY + 5}" '
             f'fill="{DIM}"/>')
    return (
        f'<line x1="{x1}" y1="{CY}" x2="{x2 - 8}" y2="{CY}" '
        f'stroke="#30363d" stroke-width="2"/>{arrow}'
        f'<text x="{mid}" y="{CY - 12}" text-anchor="middle" class="llabel">'
        f'{label}</text>'
    )


def build():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Backend request flow: Client to API to Cache to Database">',
        "<style>"
        "text{font-family:ui-monospace,'DejaVu Sans Mono',Consolas,monospace;}"
        f".title{{fill:{ACCENT};font-size:14px;font-weight:700;}}"
        f".ntitle{{fill:{FG};font-size:16px;font-weight:700;}}"
        f".nsub{{fill:{DIM};font-size:11px;}}"
        f".llabel{{fill:{DIM};font-size:10px;}}"
        "</style>",
        f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>',
        f'<text x="24" y="34" class="title">'
        f'~ $ trace request --flow</text>',
    ]

    # connectors first (behind boxes)
    for i in range(len(NODES) - 1):
        x1 = NODES[i][0] + BW / 2
        x2 = NODES[i + 1][0] - BW / 2
        parts.append(connector(x1, x2, LINK_LABELS[i]))

    for idx, (cx, title, sub) in enumerate(NODES):
        parts.append(box(cx, title, sub, idx))

    # traveling packet: halo + bright core, animated along the row
    for r, op in ((11, "0.25"), (6, "1")):
        parts.append(
            f'<circle cx="95" cy="{CY}" r="{r}" fill="{ACCENT}" opacity="{op}">'
            f'<animate attributeName="cx" dur="{DUR}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{CX_KEYTIMES}" values="{CX_VALUES}"/>'
            f'</circle>'
        )

    parts.append("</svg>")
    return "".join(parts)


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
