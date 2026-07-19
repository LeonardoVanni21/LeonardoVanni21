"""Generate a self-contained animated 'typing terminal' header SVG.

A static shell prompt is followed by phrases that type in, hold, and erase in
a loop, with a blinking caret. Pure SVG: SMIL drives the typewriter reveal,
inline CSS blinks the caret. No third-party service.
"""
import os

from config import ACCENT, BG, DIM, FG

OUT = os.path.join(os.path.dirname(__file__), "..", "typing-header.svg")

PROMPT = "leo@epicora:~$ "
PHRASES = [
    "Backend Software Engineer",
    "Cloud-native architectures on AWS",
    "High-throughput APIs with NestJS",
    "Scalable systems that ship",
]

FONT_SIZE = 22
CH = FONT_SIZE * 0.60          # monospace advance width
PAD = 22
H = 64
BASELINE = 40
CURSOR_W = CH * 0.85

# Per-phrase timing (seconds)
T_TYPE_PER = 0.09
T_ERASE_PER = 0.045
T_HOLD = 1.4
T_GAP = 0.45


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    prompt_w = len(PROMPT) * CH
    text_x = PAD + prompt_w

    # Timeline: accumulate each phrase's window into a total loop length T.
    windows = []
    t = 0.0
    for p in PHRASES:
        d = len(p) * T_TYPE_PER + T_HOLD + len(p) * T_ERASE_PER + T_GAP
        windows.append((t, len(p) * T_TYPE_PER, len(p) * T_ERASE_PER))
        t += d
    T = t

    longest = max(len(p) for p in PHRASES)
    W = int(text_x + longest * CH + CURSOR_W + PAD)

    clips, groups = [], []
    for i, p in enumerate(PHRASES):
        start, t_type, t_erase = windows[i]
        full = len(p) * CH + CURSOR_W
        k_start = start / T
        k_typed = (start + t_type) / T
        k_hold = (start + t_type + T_HOLD) / T
        k_erase = (start + t_type + T_HOLD + t_erase) / T
        key_times = f"0;{k_start:.4f};{k_typed:.4f};{k_hold:.4f};{k_erase:.4f};1"
        values = f"0;0;{full:.1f};{full:.1f};0;0"
        clips.append(
            f'<clipPath id="clip{i}"><rect x="{text_x:.1f}" y="0" '
            f'width="0" height="{H}">'
            f'<animate attributeName="width" dur="{T:.2f}s" '
            f'repeatCount="indefinite" calcMode="linear" '
            f'keyTimes="{key_times}" values="{values}"/></rect></clipPath>'
        )
        cursor_x = text_x + len(p) * CH
        groups.append(
            f'<g clip-path="url(#clip{i})">'
            f'<text x="{text_x:.1f}" y="{BASELINE}" class="typed">{esc(p)}</text>'
            f'<rect class="caret" x="{cursor_x:.1f}" y="{BASELINE - FONT_SIZE + 4}" '
            f'width="{CURSOR_W:.1f}" height="{FONT_SIZE}"/></g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="{esc(PHRASES[0])}">
  <style>
    text {{ font-family: ui-monospace, 'DejaVu Sans Mono', Consolas, monospace;
            font-size: {FONT_SIZE}px; }}
    .prompt {{ fill: {ACCENT}; font-weight: 700; }}
    .typed  {{ fill: {FG}; }}
    .caret  {{ fill: {ACCENT}; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10"
        fill="none" stroke="#21262d"/>
  <text x="{PAD}" y="{BASELINE}" class="prompt">{esc(PROMPT)}</text>
  <defs>{''.join(clips)}</defs>
  {''.join(groups)}
</svg>'''


def main():
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
