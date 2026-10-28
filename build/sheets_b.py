"""Sheets 06-09: the technical core - full elevation and three continuations.

Geometry: My_PDF.pdf page 3 (the styled orthographic elevation), re-drawn as
vectors at true metres. Figures: the dimension strings of page 2, shown at their
documented rows; levels from the level symbols. Nothing is estimated.
"""
from __future__ import annotations

import random

import cad_draw as CD
import common as C
import design as D
import lib_text as T
from design import (GOLD, GOLD_L, GRAPHITE, GRAPHITE_L, GRAY_C, GRAY_W, GRAY_WL,
                    INK, INK_SOFT, MM, PAPER, PAPER_C, WHITE)

# verified horizontal dimension chains, keyed by the CAD row they sit on
DIM_ROWS = {
    28.48: ["0.65", "5.98", "3.88"],
    25.70: ["6.30", "1.05", "2.50", "0.65"],
    24.93: ["6.30", "4.20"],
    21.34: ["8.89", "1.60"],
    17.91: ["5.30", "5.20"],
    16.36: ["5.05", "1.65", "2.50", "0.65"],
    14.07: ["6.30", "4.20"],
    10.83: ["5.35", "5.20"],
    9.07: ["0.65", "5.15", "0.50", "1.05", "2.50", "0.65"],
    3.95: ["0.65", "3.60", "3.10", "2.50", "0.65"],
    2.85: ["1.20", "2.80", "0.50", "1.20", "0.65", "0.95", "2.54", "0.65"],
}
OVERALL_W = "10.50"
TOP_LEVEL = 28.85

PAL_TECH = {
    "wall": D.Color(0.933, 0.925, 0.905),
    "shade": D.Color(0.878, 0.867, 0.841),
    "glass": D.Color(0.906, 0.925, 0.933),
    "dark": D.Color(0.157, 0.157, 0.153),
}


def fa_dim(v):
    return C.fa_digits(v).replace(".", "٫")


def dim_chain(s, x_at, y, values, fs=4.8, color=None, halo=PAPER_C, ext_from=None,
              lw=0.14):
    col = color or GRAPHITE
    cur = 0.0
    for v in values:
        a, b = x_at(cur), x_at(cur + float(v))
        s.line(a, y, b, y, color=col, lw=lw)
        for px in (a, b):
            s.line(px - 0.55, y + 0.55, px + 0.55, y - 0.55, color=col, lw=lw)
            if ext_from is not None:
                s.line(px, y + 1.4, px, ext_from, color=col, lw=0.1, dash=[0.7, 0.8])
        mid = (a + b) / 2
        txt = fa_dim(v)
        w = T.measure(txt, "fa", fs) / MM
        if halo is not None:
            s.rect(mid - w / 2 - 0.45, y - 1.45, w + 0.9, 2.4, fill=halo, stroke=None)
        s.fa(txt, fs, mid, y + 0.62, col, anchor="middle")
        cur += float(v)


def v_dim_chain(s, y_at, x, values, fs=4.8, color=None, halo=PAPER_C, lw=0.14,
                side="left"):
    col = color or GRAPHITE
    cur = 0.0
    for v in values:
        a, b = y_at(cur), y_at(cur + float(v))
        s.line(x, a, x, b, color=col, lw=lw)
        for py in (a, b):
            s.line(x - 0.55, py + 0.55, x + 0.55, py - 0.55, color=col, lw=lw)
        mid = (a + b) / 2
        txt = fa_dim(v)
        w = T.measure(txt, "fa", fs) / MM
        if halo is not None:
            s.rect(x - 1.25, mid - w / 2 - 0.6, 2.5, w + 1.2, fill=halo, stroke=None)
        s.fa(txt, fs, x, mid + w / 2, col, anchor="start", rot=90)
        cur += float(v)


def level_chain(s, x, y_at, levels, fs=5.0, color=None, side="right", bar=True,
                label=True):
    col = color or INK_SOFT
    for lv, txt in levels:
        yy = y_at(lv)
        s.line(x - 1.3, yy, x, yy, color=col, lw=0.16)
        s.line(x, yy - 1.1, x, yy + 1.1, color=col, lw=0.16)
        if label:
            s.fa(txt, fs, x + 1.6, yy + 0.6, col, font="fa-light", anchor="start")
    if bar:
        s.line(x, y_at(levels[0][0]), x, y_at(levels[-1][0]), color=INK, lw=0.28)
        s.line(x, y_at(levels[0][0]), x + 1.3, y_at(levels[0][0]), color=INK, lw=0.28)
        s.line(x, y_at(levels[-1][0]), x + 1.3, y_at(levels[-1][0]), color=INK, lw=0.28)


def chain_rows(s, rows, x_at, y_at, fs=4.5, halo=PAPER_C, dy=-1.6):
    for lv, vals in rows.items():
        dim_chain(s, x_at, y_at(lv) + dy, vals, fs=fs, halo=halo)


def note_block(s, lines, x, y, w, color=INK_SOFT, fs=6.2, gap=4.4, head=None):
    yy = y
    if head:
        s.fa(head, 6.4, x, yy, INK, font="fa-med")
        yy += gap + 1.0
    for ln in lines:
        s.fa(ln, fs, x, yy, color, font="fa-light")
        yy += gap
    return yy


# --------------------------------------------------------------------------- #
def s06(path, out_dir):
    s = D.Sheet(path, bg=PAPER_C)
    sc = 10.0
    x0, top = 58, 70
    y_at = lambda v: top + (TOP_LEVEL - v) * sc
    x_at = lambda v: x0 + v * sc
    dw = 10.85 * sc

    CD.draw_elevation(s, x0, top, sc, y_from=0, y_to=TOP_LEVEL, x_from=-0.1, x_to=10.75,
                      poche=PAL_TECH, hatch=True, line_ink=INK)

    # documented top chain + overall width
    s.fa("ردیف اندازه‌گذاری تراز +۲۸٫۴۸", 4.6, x0 + dw, y_at(28.48) - 8.6, GRAPHITE,
         anchor="end", font="fa-light")
    dim_chain(s, x_at, y_at(28.48) - 5.4, DIM_ROWS[28.48], fs=4.6)
    yy = y_at(0) + 9
    for xx in (x_at(0), x_at(10.5)):
        s.line(xx, yy - 2.2, xx, y_at(0) + 1.2, color=GRAPHITE, lw=0.1, dash=[0.8, 0.9])
    dim_chain(s, x_at, yy, [OVERALL_W], fs=5.4)
    s.fa("عرض نمای اصلی", 4.8, x_at(5.25), yy + 4.2, GRAPHITE, anchor="middle",
         font="fa-light")

    # vertical chain of documented floor-to-floor heights, left
    v_dim_chain(s, y_at, x0 - 8, ["3.00", "3.55", "3.55", "3.55", "3.55", "3.55",
                                  "3.45", "3.65", "1.00"], fs=4.4)
    s.fa("ارتفاع طبقه", 5.0, x0 - 8, y_at(0) + 26, GRAPHITE, anchor="start",
         font="fa-light", rot=90)

    # level chain + editorial zones, right
    level_chain(s, x0 + dw + 12, y_at, CD.LEVELS, fs=5.0)
    for k, a, b in (("A", TOP_LEVEL, 20.75), ("B", 20.75, 10.10), ("C", 10.10, 0.0)):
        ya, yb = y_at(a), y_at(b)
        s.line(212, ya, 212, yb, color=GOLD, lw=0.5)
        s.line(212, ya, 216, ya, color=GOLD, lw=0.5)
        s.line(212, yb, 216, yb, color=GOLD, lw=0.5)
        s.fa(k, 6.4, 219, ya + 6, GOLD, font="fa-med")
        s.fa({"A": "بخش فوقانی", "B": "بخش میانی", "C": "بخش پایینی"}[k], 5.2, 226,
             ya + 6, INK_SOFT, font="fa-light")

    # locator + drawing notes, right column
    CD.locator(s, 240, 78, 17, 56)
    for k, yy2 in (("A", 78 + 8), ("B", 78 + 30), ("C", 78 + 52)):
        s.fa(k, 5.6, 240 + 20, yy2, GOLD, font="fa-med")
    s.fa("مقیاس ۱:۱۰۰", 4.8, 257, 142, GRAPHITE, font="fa-light")
    s.fa("نمای جنوبی", 4.8, 240, 142, GRAPHITE, font="fa-light")
    note_block(s, ["ترسیم ارتوگرافیک از فایل مرجع CAD.",
                   "هیچ خطی دستی یا حدسی افزوده نشده.",
                   "اندازه‌ها روی ردیف مستند نقشه.",
                   "مقادیر ناموجود خالی مانده‌اند."],
               240, 168, 36, fs=5.3, gap=4.4, head="یادداشت نقشه")
    s.line(240, 196, 276, 196, color=GRAY_W, lw=0.25)
    s.fa("ترازها: پایه ±۰٫۰۰ تا +۲۸٫۸۵", 5.0, 276, 202, INK_SOFT, anchor="end",
         font="fa-light")
    s.fa("ارتفاع کل: ۲۸٫۸۵ متر", 5.0, 276, 208.6, INK_SOFT, anchor="end",
         font="fa-light")

    # ---- wide photographic band at the foot ----
    C.image(s, "s06_band.jpg", 24, 366, 252, 34)
    s.line(24, 362.6, 276, 362.6, color=GOLD, lw=0.25, opacity=0.85)
    s.en("PHOTOGRAPHIC REFERENCE / BALCONY RHYTHM OF THE SAME FACADE", 4.6, 24,
         359, GRAPHITE, tracking=0.14)
    # gold thread from the band up to the base of the orthographic elevation
    s.poly([(186, 366), (180, 352), (x0 + dw - 4, y_at(0) + 10), (x0 + dw - 4, y_at(0) + 1.6)],
           color=GOLD, lw=0.35, smooth=True, opacity=0.55)

    # ---- title block ----
    s.fa("نمای کامل ساختمان", 21, 276, 28, INK, anchor="end")
    s.fa("ترسیم ارتوگرافیک و مرجع اندازه‌گذاری", 9.2, 276, 39, INK_SOFT, anchor="end",
         font="fa-light")
    s.line(198, 45, 276, 45, color=GOLD, lw=0.45)
    s.en("FULL ELEVATION / TECHNICAL REFERENCE", 5.8, 276, 52, GRAPHITE, anchor="end",
         tracking=0.18, font="en-med")
    s.en("01 — ORTHOGRAPHIC ELEVATION", 5.4, 24, 28, GRAPHITE, tracking=0.16)
    s.line(24, 32, 62, 32, color=GRAY_W, lw=0.3)
    s.fa("مبنای ترسیم: فایل مرجع CAD", 6.6, 24, 39, INK_SOFT, font="fa-light")
    s.fa("نمای جنوبی؛ بدون هیچ‌گونه تغییر هندسی.", 6.2, 24, 46, GRAPHITE, font="fa-light")
    C.footer(s, 6, "نمای کامل فنی")
    s.save()


# --------------------------------------------------------------------------- #
ZONE = {"A": (20.75, 28.85), "B": (10.10, 20.75), "C": (0.00, 10.10)}


def zone_stack(s, x, y, w, h, active, rng=None):
    """Three-zone stack drawn from the real elevation, active zone highlighted."""
    rng = rng or random.Random(5)
    zones = [("A", 28.85, 20.75), ("B", 20.75, 10.10), ("C", 10.10, 0.0)]
    total = 28.85
    for k, top, bot in zones:
        hh = h * (top - bot) / total
        yy = y + h * (total - top) / total
        on = (k == active)
        s.rect(x, yy, w, hh, fill=INK if on else D.Color(0.93, 0.925, 0.905),
               stroke=None, opacity=1.0 if on else 0.9)
        s.rect(x, yy, w, hh, fill=None, stroke=GRAPHITE_L, lw=0.2)
        s.fa(k, 5.6, x + w + 2.4, yy + hh * 0.5 + 1.6, INK if on else GRAPHITE,
             font="fa-med")
    # one thin vertical accent on the active zone
    for k, top, bot in zones:
        if k != active:
            continue
        hh = h * (top - bot) / total
        yy = y + h * (total - top) / total
        s.line(x - 2.6, yy, x - 2.6, yy + hh, color=GOLD, lw=0.6)


def scale_bar(s, x, y, sc, metres=5, color=None, label=True):
    col = color or GRAPHITE
    seg = sc  # 1 m
    for i in range(metres):
        s.rect(x + i * seg, y, seg, 1.6, fill=INK if i % 2 == 0 else WHITE,
               stroke=None, opacity=0.85 if i % 2 == 0 else 1.0)
    s.line(x, y, x + metres * seg, y, color=col, lw=0.2)
    s.line(x, y + 1.6, x + metres * seg, y + 1.6, color=col, lw=0.2)
    for i in range(metres + 1):
        s.fa(C.fa_digits(str(i)), 4.4, x + i * seg, y + 5.4, col, anchor="middle",
             font="fa-light")
    if label:
        s.en("SCALE / METRES", 4.2, x + metres * seg + 4, y + 1.4, GRAPHITE,
             tracking=0.14)


def zone_sheet(path, key, title_fa, subtitle_fa, annotation_fa, footer_fa,
               en_label, rows, photo, photo_xywh, n, cut_lines,
               notes, photo_note, vchain, sc, notes_y=262):
    s = D.Sheet(path, bg=PAPER_C)
    z0, z1 = ZONE[key]
    top = 78
    x0 = 38
    y_at = lambda v: top + (z1 - v) * sc
    x_at = lambda v: x0 + v * sc
    dw = 10.85 * sc
    dh = (z1 - z0) * sc
    ybot = top + dh

    CD.draw_elevation(s, x0, top, sc, y_from=z0, y_to=z1, x_from=-0.1, x_to=10.75,
                      poche=PAL_TECH, hatch=True)

    # documented chain above the drawing
    lv = max(rows)
    s.fa(f"ردیف اندازه‌گذاری تراز +{C.fa_digits(str(lv)).replace('.', '٫')}", 4.6,
         x0 + dw, y_at(lv) - 8.8, GRAPHITE, anchor="end", font="fa-light")
    dim_chain(s, x_at, y_at(lv) - 5.4, rows[lv], fs=4.8)
    # overall width below
    yy = ybot + 10
    for xx in (x_at(0), x_at(10.5)):
        s.line(xx, yy - 2.2, xx, ybot + 1.4, color=GRAPHITE, lw=0.1, dash=[0.8, 0.9])
    dim_chain(s, x_at, yy, [OVERALL_W], fs=5.2)
    s.fa("عرض کل نما", 4.8, x_at(5.25), yy + 4.2, GRAPHITE, anchor="middle",
         font="fa-light")

    # vertical + level chains
    v_dim_chain(s, y_at, x0 - 9, vchain, fs=4.5)
    level_chain(s, x0 + dw + 11, y_at,
                [(lv2, t) for lv2, t in CD.LEVELS if z0 - 0.01 <= lv2 <= z1 + 0.01],
                fs=5.0)

    # continuity line at the shared level
    for lv2, lbl in cut_lines:
        yyy = y_at(lv2)
        s.line(x0 - 12, yyy, x0 + dw + 3, yyy, color=GOLD, lw=0.55)
        for dx in (x0 - 12, x0 + dw + 3):
            s.line(dx, yyy - 2.2, dx, yyy + 2.2, color=GOLD, lw=0.55)

    # scale bar under the drawing
    scale_bar(s, x0, ybot + 20, sc, metres=4)

    # ---- right-hand analytical column: the three-zone stack --------------
    sw, sh = 15, 108
    sx = min(x0 + dw + 17, 258)
    sy = 96
    s.fa("موقعیت محدوده در نمای کامل", 5.6, sx + sw, sy - 4, INK, anchor="end",
         font="fa-light")
    zone_stack(s, sx, sy, sw, sh, key)
    s.line(sx + sw + 9, sy, sx + sw + 9, sy + sh, color=GRAY_W, lw=0.22)
    s.fa("تراز +۲۸٫۸۵", 4.4, sx + sw + 11, sy + 1.6, GRAPHITE, font="fa-light")
    s.fa("تراز ±۰٫۰۰", 4.4, sx + sw + 11, sy + sh, GRAPHITE, font="fa-light")

    # ---- lower field: photo band + notes --------------------------------
    px, py, pw, ph = photo_xywh
    C.image(s, photo, px, py, pw, ph)
    s.line(px, py - 2.8, px + pw, py - 2.8, color=GOLD, lw=0.25)
    s.fa(photo_note, 5.4, px, py - 4.2, GRAPHITE, font="fa-light")

    note_block(s, notes, sx - 2, notes_y, 44, fs=5.6, gap=6.2, head="یادداشت فنی")

    # ---- text ----
    s.fa(title_fa, 19, 276, 28, INK, anchor="end")
    s.fa(subtitle_fa, 9.0, 276, 38.5, INK_SOFT, anchor="end", font="fa-light")
    s.line(206, 44, 276, 44, color=GOLD, lw=0.45)
    s.en(en_label, 5.8, 276, 51, GRAPHITE, anchor="end", tracking=0.18, font="en-med")
    s.en(f"{n:02d} — ELEVATION STUDIES", 5.2, 24, 28, GRAPHITE, tracking=0.16)
    s.line(24, 32, 56, 32, color=GRAY_W, lw=0.3)
    note_block(s, ["مبنای ترسیم: فایل مرجع CAD"] + notes[:1], 24, 39, 150, fs=5.8,
               gap=4.2)
    s.line(24, 52.4, 30, 52.4, color=GOLD, lw=0.5)
    s.fa(annotation_fa, 5.4, 24, 58, GOLD, font="fa-light")
    C.footer(s, n, footer_fa)
    s.save()


def s07(path, out_dir):
    zone_sheet(
        path, "A", "بزرگ‌نمایی فنی | بخش فوقانی",
        "محدوده A — قاب روشن، بازشوها و ترازهای فوقانی",
        "خط برش منطبق با ادامه نمای میانی",
        "بزرگ‌نمایی فنی / بخش فوقانی", "ENLARGED ELEVATION / UPPER ZONE",
        {28.48: DIM_ROWS[28.48], 25.70: DIM_ROWS[25.70]},
        "s07_detail.jpg", (24, 256, 152, 104.5), 7,
        cut_lines=[(20.75, "")],
        notes=["سطح فوقانی، قاب پیوسته و بازشوها بدون تغییر بازترسیم شده‌اند.",
               "اندازه‌های موضعی از ردیف‌های اندازه‌گذاری فایل CAD خوانده شده‌اند.",
               "هیچ بازشو یا جزئیات اجرایی حدس زده نشده است."],
        photo_note="برش جزئی از پوسته فوقانی", sc=17.0, notes_y=262,
        vchain=["3.45", "3.65", "1.00"])


def s08(path, out_dir):
    zone_sheet(
        path, "B", "بزرگ‌نمایی فنی | بخش میانی",
        "محدوده B — ریتم طبقات و پیوستگی پوسته",
        "تداوم هندسی با بخش فوقانی و پایینی",
        "بزرگ‌نمایی فنی / بخش میانی", "ENLARGED ELEVATION / MIDDLE ZONE",
        {21.34: DIM_ROWS[21.34], 17.91: DIM_ROWS[17.91],
         16.36: DIM_ROWS[16.36], 14.07: DIM_ROWS[14.07]},
        "s08_band.jpg", (24, 296, 176, 57.2), 8,
        cut_lines=[(20.75, ""), (10.10, "")],
        notes=["مرز فوقانی منطبق با تراز پایین محدوده A است.",
               "مرز پایینی منطبق با تراز بالای محدوده C است.",
               "هیچ طبقه‌ای در مرزها حذف یا تکرار نشده است."],
        photo_note="ریتم میانی پوسته و بالکن‌ها", sc=17.2, notes_y=292,
        vchain=["3.55", "3.55", "3.55"])


def s09(path, out_dir):
    zone_sheet(
        path, "C", "بزرگ‌نمایی فنی | بخش پایینی",
        "محدوده C — تراز پایه و ابعاد موضعی",
        "پایان مجموعه بزرگ‌نمایی‌های نما",
        "بزرگ‌نمایی فنی / بخش پایینی", "ENLARGED ELEVATION / LOWER ZONE",
        {3.95: DIM_ROWS[3.95], 2.85: DIM_ROWS[2.85]},
        "s09_base.jpg", (24, 288, 74, 84), 9,
        cut_lines=[(10.10, "")],
        notes=["تراز ±۰٫۰۰ مرجع تمام اندازه‌های ارتفاعی است.",
               "هیچ ورودی، پارکینگ یا جزئیات پایه‌ای به نقشه افزوده نشده است.",
               "اندازه‌های ناموجود عمداً خالی گذاشته شده‌اند."],
        photo_note="بخش پایینی پوسته", sc=17.2, notes_y=292,
        vchain=["3.00", "3.55", "3.55"])
