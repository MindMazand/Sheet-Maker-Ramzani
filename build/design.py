"""Editorial design system for the A3 facade monograph.

All geometry in millimetres with a top-left origin (design-tool convention).
Everything is emitted as real vector PDF plus placed raster plates, so the
sheets print at 300 DPI with crisp type and linework.
"""
from __future__ import annotations

import math
import os
import random

from reportlab.lib.colors import Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

import lib_text as T

MM = 2.8346456692913385
W, H = 297.0, 420.0

# --------------------------------------------------------------------------- #
# palette
# --------------------------------------------------------------------------- #
PAPER = Color(0.973, 0.959, 0.933)        # warm ivory paper  #F8F5EE
PAPER_L = Color(0.986, 0.978, 0.961)      # pale ivory
PAPER_C = Color(0.965, 0.969, 0.972)      # cool white       #F6F7F8
WHITE = Color(1, 1, 1)
INK = Color(0.137, 0.137, 0.133)          # charcoal         #232322
INK_SOFT = Color(0.290, 0.290, 0.278)
GRAPHITE = Color(0.420, 0.420, 0.408)
GRAPHITE_L = Color(0.600, 0.600, 0.588)
GOLD = Color(0.694, 0.557, 0.325)         # champagne        #B18E53
GOLD_L = Color(0.800, 0.686, 0.470)
GOLD_PALE = Color(0.870, 0.800, 0.660)
GRAY_W = Color(0.847, 0.827, 0.788)       # warm poche
GRAY_WL = Color(0.925, 0.914, 0.886)
GRAY_C = Color(0.780, 0.792, 0.800)
MIDNIGHT = Color(0.086, 0.125, 0.180)     # #16202E
MIDNIGHT_2 = Color(0.114, 0.161, 0.220)
BLUE_GRAY = Color(0.560, 0.616, 0.663)


def hexc(s):
    s = s.lstrip("#")
    return Color(int(s[0:2], 16) / 255, int(s[2:4], 16) / 255, int(s[4:6], 16) / 255)


# --------------------------------------------------------------------------- #
# sheet
# --------------------------------------------------------------------------- #
class Sheet:
    def __init__(self, path, bg=PAPER, w=W, h=H):
        self.path = path
        self.w, self.h = w, h
        self.c = canvas.Canvas(path, pagesize=(w * MM, h * MM))
        self.c.setTitle("Facade Design Monograph — Ramzani Residence")
        self.c.setAuthor("Radco Deco Group / MajidEisapour")
        self.c.setSubject("Architectural facade presentation sheets, A3")
        self.c.setCreator("facade monograph build")
        self.bg = bg
        self.rect(0, 0, w, h, fill=bg, stroke=None)

    # ---------------- coordinate helpers ----------------
    def X(self, x):
        return x * MM

    def Y(self, y):
        return (self.h - y) * MM

    # ---------------- primitives ----------------
    def rect(self, x, y, w, h, fill=None, stroke=None, lw=0.3, radius=0,
             opacity=None, stroke_opacity=None, dash=None, fill_alpha=None):
        c = self.c
        c.saveState()
        if fill is not None:
            c.setFillColor(fill)
            if fill_alpha is not None:
                c.setFillAlpha(fill_alpha)
            elif opacity is not None:
                c.setFillAlpha(opacity)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
            if stroke_opacity is not None:
                c.setStrokeAlpha(stroke_opacity)
            if dash:
                c.setDash([d * MM for d in dash])
        yb = self.Y(y + h)
        if radius:
            c.roundRect(self.X(x), yb, w * MM, h * MM, radius * MM,
                        stroke=1 if stroke is not None else 0,
                        fill=1 if fill is not None else 0)
        else:
            c.rect(self.X(x), yb, w * MM, h * MM,
                   stroke=1 if stroke is not None else 0,
                   fill=1 if fill is not None else 0)
        c.restoreState()

    def line(self, x1, y1, x2, y2, color=INK, lw=0.3, dash=None, opacity=None,
             cap=0, arrow=None, arrow_size=1.6):
        c = self.c
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(lw)
        if opacity is not None:
            c.setStrokeAlpha(opacity)
        if dash:
            c.setDash([d * MM for d in dash])
        c.setLineCap(cap)
        p = c.beginPath()
        p.moveTo(self.X(x1), self.Y(y1))
        p.lineTo(self.X(x2), self.Y(y2))
        c.drawPath(p, stroke=1, fill=0)
        if arrow:
            self._arrow(x1, y1, x2, y2, color, arrow_size, opacity, at="end")
        c.restoreState()

    def _arrow(self, x1, y1, x2, y2, color, size, opacity=None, at="end"):
        c = self.c
        ang = math.atan2(y2 - y1, x2 - x1)
        px, py = (x2, y2) if at == "end" else (x1, y1)
        back = ang + math.pi if at == "end" else ang
        for s in (+1, -1):
            a = back + s * 0.30
            c.saveState()
            c.setStrokeColor(color)
            c.setLineWidth(0.24)
            if opacity is not None:
                c.setStrokeAlpha(opacity)
            p = c.beginPath()
            p.moveTo(self.X(px), self.Y(py))
            p.lineTo(self.X(px + math.cos(a) * size), self.Y(py + math.sin(a) * size))
            c.drawPath(p, stroke=1, fill=0)
            c.restoreState()

    def poly(self, pts, color=INK, lw=0.35, fill=None, dash=None, opacity=None,
             close=False, smooth=False, cap=1, join=1):
        """Polyline / smooth (Catmull-Rom) path through points in mm."""
        if len(pts) < 2:
            return
        c = self.c
        c.saveState()
        p = c.beginPath()
        if smooth:
            P = [pts[0]] + list(pts) + [pts[-1]]
            p.moveTo(self.X(P[1][0]), self.Y(P[1][1]))
            for i in range(1, len(P) - 2):
                p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
                c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
                c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
                p.curveTo(self.X(c1[0]), self.Y(c1[1]), self.X(c2[0]), self.Y(c2[1]),
                          self.X(p2[0]), self.Y(p2[1]))
        else:
            p.moveTo(self.X(pts[0][0]), self.Y(pts[0][1]))
            for q in pts[1:]:
                p.lineTo(self.X(q[0]), self.Y(q[1]))
        if close:
            p.close()
        if fill is not None:
            c.setFillColor(fill)
            if opacity is not None:
                c.setFillAlpha(opacity)
        if color is not None:
            c.setStrokeColor(color)
            c.setLineWidth(lw)
            if opacity is not None:
                c.setStrokeAlpha(opacity)
            if dash:
                c.setDash([d * MM for d in dash])
        c.setLineCap(cap)
        c.setLineJoin(join)
        c.drawPath(p, stroke=1 if color is not None else 0, fill=1 if fill is not None else 0)
        c.restoreState()

    def circle(self, x, y, r, fill=None, stroke=None, lw=0.3, opacity=None):
        c = self.c
        c.saveState()
        if fill is not None:
            c.setFillColor(fill)
            if opacity is not None:
                c.setFillAlpha(opacity)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
        c.circle(self.X(x), self.Y(y), r * MM,
                 stroke=1 if stroke is not None else 0,
                 fill=1 if fill is not None else 0)
        c.restoreState()

    def image(self, path, x, y, w, h, radius=0, opacity=None, border=None,
              border_color=None, border_lw=0.3):
        c = self.c
        c.saveState()
        if radius:
            p = c.beginPath()
            p.roundRect(self.X(x), self.Y(y + h), w * MM, h * MM, radius * MM, 0, 1)
            c.clipPath(p, stroke=0, fill=0)
        if opacity is not None:
            c.setFillAlpha(opacity)
        try:
            c.drawImage(ImageReader(path), self.X(x), self.Y(y + h), w * MM, h * MM,
                        mask="auto")
        except Exception:
            c.drawImage(path, self.X(x), self.Y(y + h), w * MM, h * MM, mask="auto")
        c.restoreState()
        if border is not None:
            self.rect(x, y, w, h, fill=None, stroke=border_color or border,
                      lw=border_lw, radius=radius)

    def image_rot(self, path, x, y, w, h, deg=0, opacity=None):
        """Image rotated about its top-left corner (deg, clockwise)."""
        c = self.c
        c.saveState()
        c.translate(self.X(x), self.Y(y))
        c.rotate(-deg)
        if opacity is not None:
            c.setFillAlpha(opacity)
        c.drawImage(ImageReader(path), 0, -h * MM, w * MM, h * MM, mask="auto")
        c.restoreState()

    def clip_rect(self, x, y, w, h, radius=0):
        c = self.c
        p = c.beginPath()
        if radius:
            p.roundRect(self.X(x), self.Y(y + h), w * MM, h * MM, radius * MM, 0, 1)
        else:
            p.rect(self.X(x), self.Y(y + h), w * MM, h * MM)
        c.clipPath(p, stroke=0, fill=0)

    # ---------------- typography ----------------
    def fa(self, text, size, x, y, color=INK, anchor="start", tracking=0.0,
           opacity=None, **kw):
        return T.draw_text(self.c, text, kw.get("font", "fa"), size,
                           self.X(x), self.Y(y), color, anchor=anchor,
                           tracking_em=tracking, opacity=opacity,
                           force_base=kw.get("base"), angle=kw.get("rot", 0.0))

    def fa_block(self, text, size, x_right, y_first, max_w, color=INK,
                 gap=1.62, font="fa", tracking=0.0, opacity=None):
        lines = T.wrap(text, font, size, max_w * MM, tracking)
        y = y_first
        for ln in lines:
            w = T.measure(ln, font, size, tracking)
            T.draw_text(self.c, ln, font, size, self.X(x_right) - w, self.Y(y), color,
                        opacity=opacity, tracking_em=tracking)
            y += size / MM * gap
        return y

    def en(self, text, size, x, y, color=INK, anchor="start", tracking=0.0,
           opacity=None, font="en", base="L"):
        return T.draw_text(self.c, text, font, size, self.X(x), self.Y(y), color,
                           anchor=anchor, tracking_em=tracking, opacity=opacity,
                           force_base=base)

    # ---------------- editorial furniture ----------------
    def hairline(self, x1, y1, x2, y2, color=GOLD, lw=0.35, opacity=None):
        self.line(x1, y1, x2, y2, color=color, lw=lw, opacity=opacity)

    def pencil(self, pts, rng=None, color=GRAPHITE, lw=0.26, passes=2,
               jitter=0.35, smooth=True, opacity=0.85, taper=True):
        """Hand-drawn graphite feel: jittered double stroke with tapered ends."""
        rng = rng or random.Random(7)
        n = len(pts)
        if smooth and n >= 3:
            dense = []
            for i in range(n - 1):
                p0 = pts[max(i - 1, 0)]
                p1, p2 = pts[i], pts[i + 1]
                p3 = pts[min(i + 2, n - 1)]
                for t in [k / 6.0 for k in range(6)]:
                    t2, t3 = t * t, t * t * t
                    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                               (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                               (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                               (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                               (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                    dense.append((x, y))
            dense.append(pts[-1])
        else:
            dense = list(pts)
        for k in range(passes):
            j = jitter * (1.0 if k == 0 else 2.0)
            out = [(x + rng.gauss(0, j * 0.5), y + rng.gauss(0, j * 0.5)) for x, y in dense]
            if taper and len(out) > 8:
                for seg in range(len(out) - 1):
                    t = seg / (len(out) - 2)
                    a = opacity * (0.35 + 0.65 * math.sin(math.pi * min(1, max(0, t))))
                    self.line(out[seg][0], out[seg][1], out[seg + 1][0], out[seg + 1][1],
                              color=color, lw=lw * (0.7 + 0.5 * math.sin(math.pi * t)),
                              opacity=a, cap=1)
            else:
                self.poly(out, color=color, lw=lw, opacity=opacity, cap=1)

    def ticks(self, x, y, w=2.2, h=2.2, color=GOLD, lw=0.3):
        self.line(x, y - h, x, y + h, color=color, lw=lw)
        self.line(x - w, y, x + w, y, color=color, lw=lw)

    def level_marker(self, x, y, w=9, color=INK, lw=0.25, length=None):
        """Architectural level symbol: down-pointing triangle on a leader."""
        ln = length if length is not None else 0
        if ln:
            self.line(x, y, x - ln, y, color=color, lw=lw)
        p = [(x, y), (x - w * 0.5, y - w * 0.5), (x + w * 0.5, y - w * 0.5)]
        self.poly(p, color=color, lw=lw, fill=None, close=True)
        self.line(x - w, y - w, x + w, y - w, color=color, lw=lw)

    def folio(self, n, total=15, x=None, y=None, color=GRAPHITE, dark=False,
              sheet_label=True):
        x = x if x is not None else 24
        y = y if y is not None else 404
        self.en(f"{n:02d} — {total:02d}", 6.6, x, y, color, tracking=0.16, font="en-med")
        if sheet_label:
            fa_num = "".join("۰۱۲۳۴۵۶۷۸۹"[int(d)] for d in f"{n:02d}")
            self.fa(f"شیت {fa_num}", 7.2, x + 17, y, color, font="fa-light")
        return n

    def crop_marks(self, inset=9, length=5, color=GRAPHITE_L, lw=0.25):
        for (x, y, dx, dy) in [(inset, inset, 1, 1), (self.w - inset, inset, -1, 1),
                               (inset, self.h - inset, 1, -1),
                               (self.w - inset, self.h - inset, -1, -1)]:
            self.line(x, y, x + dx * length, y, color=color, lw=lw)
            self.line(x, y, x, y + dy * length, color=color, lw=lw)

    def save(self):
        self.c.showPage()
        self.c.save()
