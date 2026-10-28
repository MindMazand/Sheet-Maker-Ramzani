"""Renders the extracted CAD elevation into the editorial palette.

Every coordinate comes from My_PDF.pdf (page 3, the styled elevation, and
page 2, the dimensioned elevation). No line is invented.
"""
from __future__ import annotations

import json
import os

from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

import lib_text as T
from design import (GOLD, GOLD_L, GRAY_C, GRAY_W, GRAPHITE, GRAPHITE_L, INK,
                    INK_SOFT, MM)

HERE = os.path.dirname(os.path.abspath(__file__))
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        with open(os.path.join(HERE, "data", "cad_elev.json")) as fh:
            _DATA = json.load(fh)
    return _DATA


def dims():
    with open(os.path.join(HERE, "data", "cad.json")) as fh:
        return json.load(fh)


# verified level chain (from the CAD level symbols)
LEVELS = [(0.00, "±۰٫۰۰"), (3.00, "+۳٫۰۰"), (6.55, "+۶٫۵۵"), (10.10, "+۱۰٫۱۰"),
          (13.65, "+۱۳٫۶۵"), (17.20, "+۱۷٫۲۰"), (20.75, "+۲۰٫۷۵"), (24.20, "+۲۴٫۲۰"),
          (27.85, "+۲۷٫۸۵"), (28.85, "+۲۸٫۸۵")]

PAL = {
    "wall": Color(0.898, 0.878, 0.839),
    "shade": Color(0.827, 0.808, 0.769),
    "glass": Color(0.867, 0.906, 0.925),
    "dark": Color(0.129, 0.129, 0.125),
}


def draw_elevation(s, x0, y0, sc, y_from=0.0, y_to=28.85, x_from=-0.15, x_to=10.7,
                   fills=True, line_ink=INK, hatch=True, weights=None, clip=True,
                   opacity_fill=1.0, poche=None, kinds=None, only_hatch=False,
                   lw_scale=1.0):
    """Draw the elevation.

    x0, y0  : sheet position (mm) of model point (x=0, y=y_to)  -> top-left of frame
    sc      : mm per metre
    """
    d = data()
    weights = weights or {}
    # clip to the frame
    s.c.saveState()
    if clip:
        s.clip_rect(x0 - 1, y0 - 1, (x_to - x_from) * sc + 2, (y_to - y_from) * sc + 2)
    if fills:
        for f in d["fills"]:
            if kinds and f["k"] not in kinds:
                continue
            xs = [p[0] for p in f["p"]]
            ys = [p[1] for p in f["p"]]
            if max(ys) < y_from - 0.01 or min(ys) > y_to + 0.01:
                continue
            if max(xs) < x_from - 0.2 or min(xs) > x_to + 0.2:
                continue
            col = (poche or PAL)[f["k"]]
            pts = [(x0 + (x - x_from) * sc, y0 + (y_to - y) * sc) for x, y in f["p"]]
            s.poly(pts, color=None, fill=col, close=True, opacity=opacity_fill)
    if hatch:
        for st in d["strokes"]:
            if st["w"] not in (0.24,):
                continue
            pts = [(x0 + (x - x_from) * sc, y0 + (y_to - y) * sc) for x, y in st["p"]]
            if max(p[1] for p in pts) < y0 - 1 or min(p[1] for p in pts) > y0 + (y_to - y_from) * sc + 1:
                continue
            s.poly(pts, color=Color(0.55, 0.54, 0.51), lw=0.09, opacity=0.55)
    # line work: map the CAD weights onto editorial weights
    for st in d["strokes"]:
        w = st["w"]
        if w == 0.24:
            continue
        if only_hatch:
            continue
        if w >= 1.2:
            lw, col = weights.get("heavy", (0.52, INK if line_ink is INK else line_ink))
        elif w >= 0.8:
            lw, col = weights.get("mid", (0.34, line_ink))
        elif w >= 0.55:
            lw, col = weights.get("thin", (0.20, line_ink))
        else:
            lw, col = weights.get("fine", (0.14, line_ink))
        lw = lw * lw_scale
        pts = [(x0 + (x - x_from) * sc, y0 + (y_to - y) * sc) for x, y in st["p"]]
        if max(p[1] for p in pts) < y0 - 1 or min(p[1] for p in pts) > y0 + (y_to - y_from) * sc + 1:
            continue
        if len(pts) == 2:
            s.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=col, lw=lw)
        else:
            s.poly(pts, color=col, lw=lw, cap=1, join=1)
    s.c.restoreState()


def grounded_levels(s, x, y0, sc, y_from, y_to, length=7.0, color=None,
                    label=True, fs=5.6, align="end", gap=1.0):
    """Level chain on the left of the elevation (verified values only)."""
    col = color or INK_SOFT
    for lv, txt in LEVELS:
        if lv < y_from - 0.01 or lv > y_to + 0.01:
            continue
        yy = y0 + (y_to - lv) * sc
        s.line(x, yy, x + (length if align != "end" else length), yy, color=col, lw=0.18,
               dash=[1.4, 1.1])
        s.circle(x, yy, 0.35, fill=col)
        if label:
            s.fa(txt, fs, (x - gap) if align == "end" else (x + length + gap), yy + 1.9,
                 col, anchor="end" if align == "end" else "start")


def dim_string(s, pts, value, offset, fs=5.4, color=None, tick=0.9, rot=0,
               lw=0.16, fill_label=None):
    """Architectural dimension string with 45° ticks and centred figure."""
    col = color or GRAPHITE
    a, b = pts
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = (dx * dx + dy * dy) ** 0.5 or 1
    nx, ny = -dy / ln, dx / ln
    ax, ay = a[0] + nx * offset, a[1] + ny * offset
    bx, by = b[0] + nx * offset, b[1] + ny * offset
    s.line(ax, ay, bx, by, color=col, lw=lw)
    for (px, py) in ((ax, ay), (bx, by)):
        s.line(px - tick * 0.7, py + tick * 0.7, px + tick * 0.7, py - tick * 0.7,
               color=col, lw=lw)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    w = T.measure(value, "fa", fs)
    if fill_label is not None:
        s.rect(mx - w / 2 - 0.7, my - fs / MM * 0.72, w / MM + 1.4, fs / MM * 1.2,
               fill=fill_label, stroke=None)
    s.fa(value, fs, mx, my + fs / MM * 0.34, col, anchor="middle")


def zone_bracket(s, x, y_a, y_b, label, color=None, side="right", fs=5.4):
    """Editorial A/B/C identifier: thin gold bracket + Persian label."""
    col = color or GOLD
    s.line(x, y_a, x, y_b, color=col, lw=0.5)
    for yy in (y_a, y_b):
        s.line(x, yy, x + (2.6 if side == "right" else -2.6), yy, color=col, lw=0.5)
    s.fa(label, fs, x + (4.0 if side == "right" else -4.0), (y_a + y_b) / 2,
         col, anchor="start" if side == "right" else "end")


def locator(s, x, y, w, h, active=None, color=None):
    """Tiny complete-elevation silhouette locator with one zone highlighted."""
    col = color or GRAPHITE
    s.rect(x, y, w, h, fill=None, stroke=col, lw=0.2)
    # simple verified massing: podium + tower body
    s.rect(x + w * 0.06, y + h * 0.05, w * 0.88, h * 0.95, fill=Color(0.93, 0.93, 0.91),
           stroke=None)
    zones = {"A": (0.70, 1.00), "B": (0.30, 0.70), "C": (0.05, 0.30)}
    for k, (a, b) in zones.items():
        yy0 = y + h * (1 - b)
        hh = h * (b - a)
        if active == k:
            s.rect(x + w * 0.06, yy0, w * 0.88, hh, fill=GOLD, stroke=None, opacity=0.28)
        s.line(x + w * 0.06, yy0, x + w * 0.94, yy0, color=col, lw=0.12, dash=[0.8, 0.8])


def axo(s, x0, y0, sc, y_from, y_to, x_from, x_to, depth_mm, dy_mm,
        fills=True, poche=None, line=(0.2, INK), opacity=None, extrude=True,
        hatch_line=False, edge_dark=None):
    """Project the real CAD elevation into an axonometric with a depth offset.

    (x0, y0) is where model point (x_from, y_to, z=0) lands; depth_mm/dy_mm move
    a layer along +z. No geometry is invented: the same vectors, projected.
    """
    d = data()
    POL = {"wall": Color(0.925, 0.914, 0.892), "shade": Color(0.855, 0.843, 0.816),
           "glass": Color(0.878, 0.906, 0.918), "dark": Color(0.145, 0.145, 0.141)}

    def P(x, y, z=0.0):
        return (x0 + (x - x_from) * sc + z * depth_mm,
                y0 + (y_to - y) * sc - z * dy_mm)

    pal = poche or POL
    if fills:
        for f in d["fills"]:
            pts = [P(x, y) for x, y in f["p"]]
            s.poly(pts, color=None, fill=pal[f["k"]], close=True,
                   opacity=opacity if opacity is not None else 1.0)
            if extrude and f["k"] in ("wall", "dark"):
                # thin side face so the layer reads as a solid skin
                q = [P(x, y, 1.0) for x, y in f["p"]]
                side, n = [], len(pts)
                for i in range(n):
                    j = (i + 1) % n
                    side.append((pts[i], pts[j], q[j], q[i]))
                for a, b, c, dd in side:
                    if abs(a[0] - b[0]) < 0.05:
                        continue
                    s.poly([a, b, c, dd], color=None, close=True,
                           fill=Color(pal[f["k"]].red * 0.82, pal[f["k"]].green * 0.82,
                                      pal[f["k"]].blue * 0.82))
    for st in d["strokes"]:
        w = st["w"]
        if w == 0.24 and not hatch_line:
            continue
        lw = line[0] if w < 0.8 else line[0] * 1.6
        pts = [P(x, y) for x, y in st["p"]]
        if len(pts) == 2:
            s.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=line[1], lw=lw)
        else:
            s.poly(pts, color=line[1], lw=lw, cap=1, join=1)
