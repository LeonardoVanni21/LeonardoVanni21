"""Shared toolkit for the profile art: themes, text-to-path, SVG shell.

Text is converted to outlines with the portfolio's own fonts because GitHub's
CSP blocks @font-face (even data: URIs) inside README images.
"""
import html
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from config import USERNAME  # noqa: F401  (re-exported for the generators)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ART_DIR = os.path.join(ROOT, "art")

PAD = 44
W = 860  # every sheet shares one width so the README column stays aligned

THEMES = {
    "light": dict(
        mode="light", bg="#e8e7df", fg="#111210", muted="#606459", line="#11121030",
        soft="#dddcd2", glow="#ffffff", glowop=".8", sage="#8e9a88", deep="#374332", rust="#8e2020",
        heat=["#d7d8ce", "#c3cbb8", "#a3b09a", "#6f8268", "#374332"],
        langs=["#374332", "#6f8268", "#8e2020", "#b7a27a", "#a3b09a",
               "#606459", "#9aa08f", "#8a7f6a"],
    ),
    "dark": dict(
        mode="dark", bg="#111210", fg="#e8e7df", muted="#a0a298", line="#ffffff26",
        soft="#1a1c19", glow="#f4f6ec", glowop=".5", sage="#8e9a88", deep="#b7c9a9", rust="#d0705f",
        heat=["#1d1f1b", "#2a3427", "#44593f", "#6f8a66", "#b7c9a9"],
        langs=["#b7c9a9", "#6f8a66", "#d0705f", "#c9b48a", "#5d7a55",
               "#7d8578", "#6b7466", "#8a7f6a"],
    ),
}

_FONT_FILES = {
    "display": "Archivo-SemiBold.ttf",
    "serif": "InstrumentSerif-Regular.ttf",
    "serif-i": "InstrumentSerif-Italic.ttf",
    "mono": "SpaceMono-Regular.ttf",
    "mono-b": "SpaceMono-Bold.ttf",
}
_faces = {}


def _num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Face:
    def __init__(self, path):
        self.font = TTFont(path)
        self.upm = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()
        self.hmtx = self.font["hmtx"]

    def _gname(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap[ord("?")]

    def width(self, s, size, track=0.0):
        k = size / self.upm
        return sum(self.hmtx[self._gname(c)][0] * k + track * size for c in s)

    def glyph_path(self, g):
        pen = SVGPathPen(self.glyphs, ntos=lambda v: str(int(round(v))))
        self.glyphs[g].draw(pen)
        return pen.getCommands()


def face(name):
    if name not in _faces:
        _faces[name] = Face(os.path.join(HERE, "fonts", _FONT_FILES[name]))
    return _faces[name]


_defs = {}  # glyph id -> outline, shared by every string in one SVG


def text(font, s, x, y, size, fill, anchor="start", track=0.0, extra=""):
    f = face(font)
    if anchor == "middle":
        x -= f.width(s, size, track) / 2
    elif anchor == "end":
        x -= f.width(s, size, track)
    k = size / f.upm
    uses, cx = [], 0.0
    for c in s:
        g = f._gname(c)
        if c != " ":
            gid = f"{font.replace('-', '')}{f.font.getGlyphID(g)}"
            if gid not in _defs:
                _defs[gid] = f.glyph_path(g)
            if _defs[gid]:
                uses.append(f'<use href="#{gid}" x="{cx:g}"/>')
        cx += f.hmtx[g][0] + track * f.upm
    if not uses:
        return ""
    return (f'<g transform="matrix({k:.5f} 0 0 {-k:.5f} {x:.1f} {y:.1f})" '
            f'fill="{fill}" {extra}>{"".join(uses)}</g>')


def drain_defs():
    d = "".join(f'<path id="{i}" d="{p}"/>' for i, p in _defs.items() if p)
    _defs.clear()
    return f"<defs>{d}</defs>" if d else ""


def width(font, s, size, track=0.0):
    return face(font).width(s, size, track)


PULSE_CSS = ("@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}"
             "50%{opacity:.35;transform:scale(1.8)}}"
             ".dot{animation:pulse 2.4s ease-in-out infinite;"
             "transform-box:fill-box;transform-origin:center}")


def live_dot(t, x, y):
    return f'<circle class="dot" cx="{x}" cy="{y}" r="3.2" fill="{t["sage"]}"/>'


def head(t, left, right, live=False):
    x = PAD + (16 if live else 0)
    return ((live_dot(t, PAD + 3, 46.5) if live else "")
            + text("mono", left, x, 50, 11, t["muted"], track=0.14)
            + text("mono", right, W - PAD, 50, 11, t["muted"], "end", 0.14)
            + f'<line x1="{PAD}" x2="{W - PAD}" y1="68" y2="68" stroke="{t["line"]}"/>')


def delay(seconds):
    """Animation delay that the preview harness can shift via --t."""
    return f"animation-delay:calc({seconds:.2f}s - var(--t,0s))"


def esc(s):
    return html.escape(s, quote=True)


def sheet(w, h, body, t, css="", label="", rx=14):
    """Wrap content in a bordered sheet that matches the portfolio paper."""
    freeze = os.environ.get("ART_FREEZE")
    # Reduced motion: freeze on the finished state and drop the overlay layers.
    calm = "@media(prefers-reduced-motion:reduce){*{animation:none!important}.ov{display:none}}"
    preview = (f"svg{{--t:{freeze}s}}*{{animation-play-state:paused!important}}"
               if freeze else "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
        f"<style>{css}{calm}{preview}</style>{drain_defs()}"
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="{t["bg"]}"/>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{rx}" '
        f'fill="none" stroke="{t["line"]}"/>'
        f"{body}</svg>"
    )


def write_all(name, build):
    """Render build(theme) once per theme into art/<name>-<theme>.svg."""
    os.makedirs(ART_DIR, exist_ok=True)
    for tname, t in THEMES.items():
        path = os.path.join(ART_DIR, f"{name}-{tname}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(t))
    print(f"wrote art/{name}-{{light,dark}}.svg")
