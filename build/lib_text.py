"""Vector text engine: Persian/Latin strings -> reportlab paths.

Every string is shaped with HarfBuzz (joining + kerning + ZWNJ handling),
ordered with a minimal bidi pass, and drawn as pure outlines. No <text>, no
font embedding surprises: the sheet renders identically everywhere and stays
vector in the PDF.
"""
from __future__ import annotations

import functools
import os
import unicodedata

import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

FONTS = {
    "fa-thin": "Vazirmatn-Thin.ttf",
    "fa-xl": "Vazirmatn-ExtraLight.ttf",
    "fa-light": "Vazirmatn-Light.ttf",
    "fa": "Vazirmatn-Regular.ttf",
    "fa-med": "Vazirmatn-Medium.ttf",
    "fa-bold": "Vazirmatn-Bold.ttf",
    "en-light": "Inter-300.ttf",
    "en": "Inter-400.ttf",
    "en-med": "Inter-500.ttf",
    "en-semi": "Inter-600.ttf",
    "en-bold": "Inter-700.ttf",
}


class Face:
    def __init__(self, key):
        path = os.path.join(FONT_DIR, FONTS[key])
        with open(path, "rb") as fh:
            data = fh.read()
        self.blob = hb.Blob(data)
        self.hbfont = hb.Font(hb.Face(self.blob))
        self.upem = self.hbfont.face.upem
        self.tt = TTFont(path)
        self.glyphset = self.tt.getGlyphSet()
        self.gorder = self.tt.getGlyphOrder()
        self.cmap = self.tt.getBestCmap()
        hhea = self.tt["hhea"]
        self.ascent = hhea.ascent / self.upem
        self.descent = -hhea.descent / self.upem
        self.cap = getattr(self.tt["OS/2"], "sCapHeight", int(self.upem * 0.7)) / self.upem
        self.key = key


_FACES = {}


def face(key):
    if key not in _FACES:
        _FACES[key] = Face(key)
    return _FACES[key]


# --------------------------------------------------------------------------- #
# bidi
# --------------------------------------------------------------------------- #
def _bclass(ch):
    b = unicodedata.bidirectional(ch)
    if b in ("R", "AL"):
        return "R"
    if b == "L":
        return "L"
    if b in ("EN", "AN"):
        return "D"          # digit run: displays LTR, but counts as R for neutrals
    return "N"


def _base_dir(text):
    """Paragraph base direction: Persian letters anywhere make the line RTL."""
    for ch in text:
        c = _bclass(ch)
        if c == "R":
            return "R"
        if c == "L" and c != "D":
            return "L"
    return "L"


def _resolved(text, force_base=None):
    base = force_base or _base_dir(text)
    cls = [_bclass(ch) for ch in text]
    dirs = []
    for i, c in enumerate(cls):
        if c == "D":
            dirs.append("D")
        elif c in ("R", "L"):
            dirs.append(c)
        else:
            dirs.append(None)
    # UBA N1/N2: a neutral takes the direction of its two strong neighbours when
    # they agree, otherwise the embedding (paragraph) direction. Numbers count
    # as R for this rule.
    n = len(cls)
    for i in range(n):
        if dirs[i] is not None:
            continue
        prev = None
        for j in range(i - 1, -1, -1):
            if dirs[j] is not None:
                prev = "R" if dirs[j] == "D" else dirs[j]
                break
        nxt = None
        for j in range(i + 1, n):
            if dirs[j] is not None:
                nxt = "R" if dirs[j] == "D" else dirs[j]
                break
        if prev is not None and prev == nxt:
            dirs[i] = prev
        else:
            dirs[i] = base
    return dirs, base


def _visual_runs(text, force_base=None):
    if not text:
        return []
    dirs, base = _resolved(text, force_base)
    runs = []
    for i, ch in enumerate(text):
        d = dirs[i]
        cls = _bclass(ch)
        key = "D" if cls == "D" else d
        if runs and runs[-1][0] == key:
            runs[-1][2] = i + 1
        else:
            runs.append([key, i, i + 1])
    out = [(s, e, d == "R") for d, s, e in runs]
    if base == "R":
        out = list(reversed(out))
    return out


# --------------------------------------------------------------------------- #
# pen
# --------------------------------------------------------------------------- #
class _PathPen(BasePen):
    def __init__(self, glyphSet, ox, oy, scale):
        super().__init__(glyphSet)
        self.ox, self.oy, self.s = ox, oy, scale
        self.contours = []
        self.cur = None

    def _moveTo(self, p):
        self.cur = [("M", (self.ox + p[0] * self.s, self.oy - p[1] * self.s))]
        self.contours.append(self.cur)

    def _lineTo(self, p):
        self.cur.append(("L", (self.ox + p[0] * self.s, self.oy - p[1] * self.s)))

    def _curveToOne(self, p1, p2, p3):
        self.cur.append((
            "C",
            (self.ox + p1[0] * self.s, self.oy - p1[1] * self.s),
            (self.ox + p2[0] * self.s, self.oy - p2[1] * self.s),
            (self.ox + p3[0] * self.s, self.oy - p3[1] * self.s),
        ))

    def _closePath(self):
        if self.cur:
            self.cur.append(("Z",))


def _space_adv(f, ch):
    gid = f.cmap.get(ord(ch))
    return f.tt["hmtx"][gid][0] if gid else f.upem * 0.25


def glyph_runs(text, font_key, size, tracking_em=0.0, force_base=None):
    """Return list of (contours, advance) laid out from x=0, y=0 (baseline)."""
    f = face(font_key)
    scale = size / f.upem
    out = []
    x = 0.0
    for start, end, rtl in _visual_runs(text, force_base):
        chunk = text[start:end]
        if not chunk.strip():
            adv = sum(_space_adv(f, ch) for ch in chunk) * scale
            if out:
                prev = out[-1]
                out[-1] = (prev[0], prev[1] + adv)
            else:
                out.append((None, adv))
            x += adv
            continue
        buf = hb.Buffer()
        buf.add_str(chunk)
        buf.guess_segment_properties()
        buf.direction = "rtl" if rtl else "ltr"
        hb.shape(f.hbfont, buf)
        for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
            pen = _PathPen(f.glyphset, x + pos.x_offset * scale, -pos.y_offset * scale, scale)
            f.glyphset[f.gorder[info.codepoint]].draw(pen)
            adv = pos.x_advance * scale + (tracking_em * size if i < len(buf.glyph_infos) - 1 else 0)
            out.append((pen.contours, adv))
            x += adv
    return out, x


@functools.lru_cache(maxsize=16384)
def measure(text, font_key, size, tracking_em=0.0, force_base=None):
    runs, w = glyph_runs(text, font_key, size, tracking_em, force_base)
    return w


def wrap(text, font_key, size, max_w, tracking_em=0.0):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w) if cur else w
        if measure(trial, font_key, size, tracking_em) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw(c, runs, x, y, fill, opacity=None, angle=0.0):
    for contours, _adv in runs:
        if not contours:
            continue
        p = c.beginPath()
        for cont in contours:
            for seg in cont:
                if seg[0] == "M":
                    p.moveTo(x + seg[1][0], y - seg[1][1])
                elif seg[0] == "L":
                    p.lineTo(x + seg[1][0], y - seg[1][1])
                elif seg[0] == "C":
                    p.curveTo(
                        x + seg[1][0], y - seg[1][1],
                        x + seg[2][0], y - seg[2][1],
                        x + seg[3][0], y - seg[3][1],
                    )
                elif seg[0] == "Z":
                    p.close()
        c.saveState()
        c.setFillColor(fill)
        if opacity is not None:
            c.setFillAlpha(opacity)
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()


def draw_text(c, text, font_key, size, x, y, fill, anchor="start", tracking_em=0.0,
              opacity=None, leading=None, force_base=None, angle=0.0):
    """Draw a single line; (x, y) is the baseline in *points*, y grows up.

    angle rotates the string counter-clockwise around (x, y).
    """
    runs, w = glyph_runs(text, font_key, size, tracking_em, force_base)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    if abs(angle) < 1e-6:
        _draw(c, runs, x, y, fill, opacity)
        return w
    import math as _m
    a = _m.radians(angle)
    ca, sa = _m.cos(a), _m.sin(a)

    class _Rot:
        def __init__(self, cx, cy):
            self.cx, self.cy = cx, cy

        def __call__(self, px, py):
            return (self.cx + px * ca - py * sa, self.cy + px * sa + py * ca)

    # rotate every contour point about the baseline origin
    rot_runs = []
    for contours, adv in runs:
        if not contours:
            rot_runs.append((contours, adv))
            continue
        new = []
        for cont in contours:
            nc = []
            for seg in cont:
                if seg[0] in ("M", "L"):
                    px, py = seg[1]
                    nc.append((seg[0], (px * ca - py * sa, px * sa + py * ca)))
                elif seg[0] == "C":
                    nc.append(("C", (seg[1][0] * ca - seg[1][1] * sa, seg[1][0] * sa + seg[1][1] * ca),
                               (seg[2][0] * ca - seg[2][1] * sa, seg[2][0] * sa + seg[2][1] * ca),
                               (seg[3][0] * ca - seg[3][1] * sa, seg[3][0] * sa + seg[3][1] * ca)))
                else:
                    nc.append(seg)
            new.append(nc)
        rot_runs.append((new, adv))
    _draw(c, rot_runs, x, y, fill, opacity)
    return w


def draw_block(c, text, font_key, size, x_right, y_top, max_w, fill, line_gap=1.55,
               tracking_em=0.0, opacity=None, align="right"):
    """Right-aligned wrapped paragraph. y_top = baseline of first line."""
    lines = wrap(text, font_key, size, max_w, tracking_em)
    y = y_top
    for ln in lines:
        runs, w = glyph_runs(ln, font_key, size, tracking_em)
        xx = x_right - w if align == "right" else x_right
        _draw(c, runs, xx, y, fill, opacity)
        y -= size * line_gap
    return len(lines), y


def cap_height(font_key):
    return face(font_key).cap


def ascent(font_key):
    return face(font_key).ascent
