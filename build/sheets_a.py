"""Sheets 01-05: identity and visual experience."""
from __future__ import annotations

import json
import math
import os
import random

import cad_draw as CD
import common as C
import design as D
import lib_text as T
from design import (GOLD, GOLD_L, GOLD_PALE, GRAPHITE, GRAPHITE_L, GRAY_W, GRAY_WL, INK,
                    INK_SOFT, MIDNIGHT, MM, PAPER, PAPER_C, PAPER_L, WHITE)

A = C.A

# master photograph framing helpers -----------------------------------------
MASTER_AR = 2969 / 3804          # width / height of blank.png


def frame(x, y, w, h):
    """Return a mapper from master-relative coords to sheet mm for a plate that
    shows the whole master frame cover-fitted into (x, y, w, h)."""
    sc = max(w / MASTER_AR, h)      # mm per unit height
    vis_w = w / sc                  # visible fraction of master width
    off = (1 - vis_w) / 2

    def m(u, v):
        return ((u - off) / vis_w * w + x, y + v * h)

    return m, off


def blade(m, u0, v0, u1, v1, n=42):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(m(u0 + (u1 - u0) * t, v0 + (v1 - v0) * t))
    return pts


# --------------------------------------------------------------------------- #
def s01(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)
    hx, hy, hw, hh = 40, 0, 257, 340
    C.image(s, "s01_hero.jpg", hx, hy, hw, hh)
    m, off = frame(hx, hy, hw, hh)

    # ---- graphite contour of the real curved silhouette against the sky -----
    rng = random.Random(11)
    trace = [m(0.2905, 0.0955), m(0.2843, 0.1400), m(0.2716, 0.2190),
             m(0.2652, 0.2590), m(0.2638, 0.2980), m(0.2530, 0.3380),
             m(0.2530, 0.3760)]
    s.pencil(trace, rng=rng, color=INK, lw=0.38, jitter=0.16, passes=1, opacity=0.4,
             taper=True)
    end = m(0.2530, 0.3760)
    # the same line leaves the photograph and becomes a single champagne stroke
    # that resolves as the left rule of the title block and ends on the imprint line
    s.poly([end, (end[0], end[1] + 14), (30.4, 300), (30.4, 366), (30.4, 410.5),
            (30.4, 412.6)], color=GOLD, lw=0.6, smooth=True, cap=1)

    # faint elevation fragment of the real CAD drawing (tracing-paper whisper)
    CD.draw_elevation(s, 252, 350, 1.62, y_from=0, y_to=28.9, fills=False, hatch=True,
                      weights={"heavy": (0.1, GRAPHITE_L), "mid": (0.09, GRAPHITE_L),
                               "thin": (0.08, GRAPHITE_L), "fine": (0.07, GRAPHITE_L)})
    s.en("ELEVATION TRACE", 4.4, 252, 347, GRAPHITE, tracking=0.16)

    # secondary detail crop
    dx, dy, dw, dh = 200, 352, 46, 38
    C.image(s, "s01_detail.jpg", dx, dy, dw, dh)
    s.line(dx, dy - 3.0, dx + dw, dy - 3.0, color=GOLD, lw=0.25, opacity=0.85)
    s.en("CURVED SHELL / SOFFIT", 4.4, dx, dy + dh + 4.2, GRAPHITE, tracking=0.16)

    # ---- typography in the lower-left negative space -----------------------
    x = 48
    s.fa("طراحی پوسته و نمای ساختمان", 28.0, x, 362, INK)
    s.fa("از هویت فرمی تا منطق اجرا", 11.4, x, 374.5, INK_SOFT, font="fa-light")
    s.line(x, 380.4, x + 86, 380.4, color=GRAY_W, lw=0.4)
    s.fa("دفترچه جامع ارائه معماری", 8.0, x, 388.4, INK_SOFT, font="fa-light")
    s.fa("روایت معماری، متریال و جزئیات", 8.0, x, 396.4, GRAPHITE, font="fa-light")
    s.en("FACADE DESIGN MONOGRAPH", 6.2, x, 406, GRAPHITE, tracking=0.26, font="en-med")
    s.en("DESIGN INTENT / MATERIALITY / TECHNICAL DEVELOPMENT", 5.2, 276, 406,
         GRAPHITE, tracking=0.16, anchor="end")
    s.line(21, 412.6, 276, 412.6, color=GOLD, lw=0.3, opacity=0.55)
    s.fa("آپارتمان مسکونی رمضانی — بابلسر، مازندران", 6.2, 21, 418.4, GRAPHITE,
         font="fa-light")
    s.en("RESIDENTIAL APARTMENT / BABOLSAR", 5.2, 276, 418.4, GRAPHITE, anchor="end",
         tracking=0.16)
    s.save()


# --------------------------------------------------------------------------- #
def s02(path, out_dir):
    s = D.Sheet(path, bg=PAPER)
    px, py, pw, ph = 128, 0, 169, 420
    C.image(s, "s02_facade.jpg", px, py, pw, ph)
    m, _ = frame(px, py, pw, ph)

    # ---- title ----
    s.fa("منطق شکل‌گیری پوسته", 22, 118, 46, INK, anchor="end")
    s.fa("پیوستگی خطوط، عمق سایه و تعادل سطوح", 9.2, 118, 57, INK_SOFT, anchor="end",
         font="fa-light")
    s.en("FORM / DEPTH / RHYTHM", 6.2, 118, 66, GRAPHITE, anchor="end", tracking=0.24,
         font="en-med")
    s.line(21, 72, 118, 72, color=GOLD, lw=0.45)

    # ---- fragment 01: silhouette extracted from the master photograph ----
    C.image(s, "s02_sil.jpg", 21, 148, 50, 104)
    s.en("SILHOUETTE / FROM THE RENDER", 4.2, 21, 256, GRAPHITE, tracking=0.12)

    # ---- fragment 02: elevation band, real CAD linework ----
    s.rect(78, 148, 46, 38, fill=PAPER_L, stroke=None, opacity=0.65)
    CD.draw_elevation(s, 80, 150, 3.6, y_from=24.6, y_to=28.9, hatch=False,
                      weights={"heavy": (0.24, GRAPHITE), "mid": (0.18, GRAPHITE),
                               "thin": (0.13, INK_SOFT), "fine": (0.09, GRAPHITE_L)})
    s.en("CAD ELEVATION / UPPER BAND", 4.2, 78, 190, GRAPHITE, tracking=0.12)

    # ---- fragment 03: two photographic details ----
    C.image(s, "s02_frag1.jpg", 78, 198, 46, 32)
    C.image(s, "s02_frag2.jpg", 78, 236, 46, 30)

    # ---- labels, aligned to their fragments ----
    labels = [("۰۱ — پیوستگی قاب روشن", 262),
              ("۰۲ — عمق بصری بالکن‌ها", 276),
              ("۰۳ — ریتم افقی و عمودی", 290)]
    for i, (lb, yy) in enumerate(labels):
        C.marker(s, 23.2, yy - 1.0, C.fa_num(i + 1), r=2.2, fs=5.2)
        s.fa(lb, 7.4, 28, yy, INK, font="fa-light")
        s.line(28, yy + 2.2, 28 + 78, yy + 2.2, color=GRAY_W, lw=0.22)

    # ---- closing statement ----
    s.fa_block("هویت نما از رابطه میان قاب پیوسته، سطوح عقب‌نشسته و تغییرات نور شکل می‌گیرد.",
               8.2, 118, 330, 96, INK_SOFT, gap=1.85)

    # the analytical thread: graphite -> gold, from the analysis into the photograph
    rng = random.Random(3)
    s.pencil([(64, 244), (56, 258), (48, 274)], rng=rng, color=GRAPHITE,
             lw=0.3, jitter=0.3, passes=2, opacity=0.75)
    s.poly([(48, 274), (66, 286), (88, 300), (110, 314), (128, 326)], color=GOLD,
           lw=0.45, smooth=True, opacity=0.9)

    C.footer(s, 2, "روایت مفهومی؛ از خط تا حجم")
    s.save()


# --------------------------------------------------------------------------- #
def s03(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)
    mx, my, mw, mh = 84, 0, 213, 286
    C.image(s, "s03_macro.jpg", mx, my, mw, mh)
    m, _ = frame(mx, my, mw, mh)

    # a single graphite trace just outside the plate, following the real curve
    rng = random.Random(5)
    s.pencil([m(0.44, 0.10), m(0.40, 0.16), m(0.385, 0.24), m(0.40, 0.32)],
             rng=rng, color=GRAPHITE, lw=0.3, jitter=0.4, passes=2, opacity=0.55)

    # title, lower left
    s.fa("لمسِ فرم، خوانشِ ماده", 27, 21, 312, INK)
    s.fa("بافت عمودی، انحنای نرم و عمق سایه", 10.4, 21, 326, INK_SOFT, font="fa-light")
    s.line(21, 334, 104, 334, color=GOLD, lw=0.45)

    # panoramic soffit crop along the lower edge
    C.image(s, "s03_soffit.jpg", 21, 352, 200, 30)
    C.marker(s, 226, 358, "۰۲", r=2.2, fs=5.2)
    s.fa("سطح تیره و عقب‌نشسته", 8.0, 231, 359, INK, font="fa-light")
    s.line(227, 361, 224, 372, color=GOLD, lw=0.3)

    # label 01 on the paper margin, leader onto the genuine ribbed surface
    C.marker(s, 23.4, 84, "۰۱", r=2.2, fs=5.2)
    s.fa("پوسته روشن", 8.0, 28, 85, INK, font="fa-light")
    p = m(0.505, 0.335)
    s.poly([(58, 84), (74, 90), (p[0], p[1])], color=GOLD, lw=0.3, smooth=True)

    s.en("TACTILE STUDY / IVORY RIBBED SHELL — CHARCOAL SOFFIT", 5.6, 276, 346,
         GRAPHITE, anchor="end", tracking=0.18)
    s.fa("مطالعه بافت پوسته در مقیاس نزدیک", 6.4, 276, 340, GRAPHITE, anchor="end",
         font="fa-light")
    C.footer(s, 3, "مکث تصویری؛ پرتره متریال")
    s.save()


# --------------------------------------------------------------------------- #
def s04(path, out_dir):
    s = D.Sheet(path, bg=WHITE)
    ix, iy, iw, ih = 16, 16, 265, 352
    C.image(s, "s04_day.jpg", ix, iy, iw, ih)
    m, _ = frame(ix, iy, iw, ih)

    # corner crop overlapping the right edge, frameless
    sx, sy, sw, sh = 249, 250, 62, 35
    C.image(s, "s04_corner.jpg", sx, sy, sw, sh)
    s.line(sx - 3, sy + sh + 2, sx + sw * 0.5, sy + sh + 2, color=GOLD, lw=0.3)

    # graphite line from the top margin onto a real curved edge, then gold mark
    rng = random.Random(21)
    p0 = m(0.362, 0.076)
    s.pencil([(p0[0] + 2.0, iy - 14), (p0[0] + 0.6, iy - 4), (p0[0] - 0.4, p0[1] - 7),
              (p0[0] + 3.0, p0[1] - 1.6), (p0[0] + 12, p0[1] + 0.4)],
             rng=rng, color=GRAPHITE, lw=0.3, jitter=0.3, passes=2, opacity=0.65,
             taper=False)
    s.poly([(p0[0] + 12, p0[1] + 0.4), (p0[0] + 30, p0[1] + 6), (232, 352)],
           color=GOLD, lw=0.5, smooth=True)
    s.line(226, 350, 238, 350, color=GOLD, lw=0.5)
    for i in range(3):
        s.line(242 + i * 3.2, 347.4, 242 + i * 3.2, 352.6, color=GOLD, lw=0.3, opacity=0.85)

    # ---- title block ----
    s.fa("خوانش نهایی پوسته", 25, 276, 383, INK, anchor="end")
    s.fa("فرم پیوسته، عمق متغیر و شفافیت کنترل‌شده", 9.4, 276, 395.5, INK_SOFT,
         anchor="end", font="fa-light")
    s.fa("رندر نهایی طرح مصوب", 7.8, 276, 404.5, GRAPHITE, anchor="end", font="fa-light")
    s.en("FINAL FACADE / DAYLIGHT VIEW", 6.2, 16, 383, GRAPHITE, tracking=0.22,
         font="en-med")
    s.line(16, 390, 58, 390, color=GOLD, lw=0.45)
    s.en("01  /  REFERENCE RENDER", 5.8, 16, 398, GRAPHITE, tracking=0.18)
    s.fa("شیت ۰۴", 6.6, 16, 406, GRAPHITE, font="fa-med")
    s.save()


# --------------------------------------------------------------------------- #
def s05(path, out_dir):
    s = D.Sheet(path, bg=MIDNIGHT)
    ix, iy, iw, ih = 26, 0, 271, 352
    C.image(s, "s05_night.jpg", ix, iy, iw, ih)
    m, _ = frame(ix, iy, iw, ih)

    # small daytime crop inside the midnight field, linked by one gold thread
    cx, cy, cw, ch = 222, 300, 50, 23
    C.image(s, "s05_day_crop.jpg", cx, cy, cw, ch)
    s.rect(cx, cy, cw, ch, fill=None, stroke=GOLD, lw=0.25, opacity=0.9)
    anchor = m(0.455, 0.400)
    s.poly([(cx, cy + 3), (cx - 20, cy + 6), (anchor[0] + 8, anchor[1] + 3)],
           color=GOLD, lw=0.4, smooth=True, opacity=0.6)
    s.circle(anchor[0] + 8, anchor[1] + 3, 0.5, fill=GOLD)
    s.en("DAYLIGHT REFERENCE", 5.2, cx, cy + ch + 4.6, GOLD_L, tracking=0.2)

    # ---- typography on the midnight field ----
    light = D.Color(0.955, 0.945, 0.918)
    mid = D.Color(0.760, 0.775, 0.790)
    dim = D.Color(0.560, 0.585, 0.615)
    s.fa("معماری در ساعت آبی", 28, 276, 380, light, anchor="end")
    s.fa("خوانش شبانه عمق، نور و متریال", 10.2, 276, 393.5, mid, anchor="end",
         font="fa-light")
    s.line(206, 400, 276, 400, color=GOLD, lw=0.45)
    s.en("BLUE HOUR / ARCHITECTURAL LIGHTING", 6.0, 276, 407, GOLD_L, anchor="end",
         tracking=0.22, font="en-med")
    s.fa("نورپردازی مکمل فرم معماری است.", 7.4, 21, 372, mid, font="fa-light")
    s.fa("همان هندسه، نور دیگر", 7.0, 21, 381, dim, font="fa-light")
    s.en("02  —  DUSK STUDY", 5.6, 21, 392, dim, tracking=0.18)
    s.fa("شیت ۰۵", 6.6, 21, 401, dim, font="fa-med")
    s.save()
