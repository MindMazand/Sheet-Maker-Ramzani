"""Sheets 10-15: material, detail, axonometric, urban context, sequence, closing."""
from __future__ import annotations

import math
import os
import random

import cad_draw as CD
import common as C
import design as D
import lib_text as T
from design import (GOLD, GOLD_L, GOLD_PALE, GRAPHITE, GRAPHITE_L, GRAY_C, GRAY_W,
                    GRAY_WL, INK, INK_SOFT, MM, PAPER, PAPER_C, PAPER_L, WHITE)


# --------------------------------------------------------------------------- #
def s10(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)

    # ---- title, upper left ----
    s.fa("منطق انتخاب متریال", 23, 130, 34, INK)
    s.fa("بافت، عمق، شفافیت و کنتراست", 9.2, 130, 46, INK_SOFT, font="fa-light")
    s.line(24, 52, 130, 52, color=GOLD, lw=0.45)
    s.en("MATERIAL ARCHIVE / SURFACE, DEPTH, TRANSPARENCY", 5.6, 24, 60, GRAPHITE,
         tracking=0.16, font="en-med")

    # ---- three photographic fields of different sizes ----
    C.image(s, "s10_rib.jpg", 24, 70, 34, 150)          # tall rib macro
    C.image(s, "s10_main.jpg", 78, 70, 198, 118)        # main facade crop
    C.image(s, "s10_glass.jpg", 24, 230, 46, 34)        # glazing at the intersection
    C.image(s, "s10_soffit.jpg", 78, 230, 176, 26)      # broad dark band

    # graphite contour over the real curved shell in the main image
    rng = random.Random(41)
    s.pencil([(196, 108), (188, 116), (186, 126), (190, 136)], rng=rng,
             color=GRAPHITE, lw=0.26, jitter=0.25, passes=2, opacity=0.5)
    s.poly([(190, 136), (184, 160), (170, 190)], color=GOLD, lw=0.3, smooth=True,
           opacity=0.7)

    # ---- material labels ----
    items = [("۰۱ — پوسته روشن شیاردار", (70, 132), (24, 276)),
             ("۰۲ — سطح تیره با رگه‌های طبیعی", (150, 243), (24, 287)),
             ("۰۳ — شیشه و بازتاب محیط", (48, 244), (24, 298)),
             ("۰۴ — پروفیل فلزی تیره", (232, 150), (24, 309)),
             ("۰۵ — پوشش گیاهی کنترل‌شده", (196, 84), (24, 320))]
    for i, (txt, tgt, lab) in enumerate(items):
        C.marker(s, lab[0] + 2.2, lab[1] - 1.0, C.fa_num(i + 1), r=2.2, fs=5.2)
        s.fa(txt, 7.2, lab[0] + 7, lab[1], INK, font="fa-light")

    # tiny numbered markers on the plates themselves
    for i, (txt, tgt, lab) in enumerate(items):
        C.marker(s, tgt[0] + 3, tgt[1], C.fa_num(i + 1), r=2.0, fs=4.6, color=WHITE,
                 ink=WHITE)
        s.poly([(lab[0] + 5, lab[1] - 1.3), (tgt[0] - 3.5, lab[1] - 1.3), (tgt[0], tgt[1])],
               color=GOLD, lw=0.22, opacity=0.5, smooth=True)

    # ---- specification fields: deliberately unfilled ----
    s.line(24, 336, 276, 336, color=GRAY_W, lw=0.3)
    fields = ["نام محصول", "ضخامت نهایی", "روش نصب", "کد تأیید متریال"]
    for i, f in enumerate(fields):
        x = 24 + i * 63
        s.fa(f, 6.2, x, 343, INK_SOFT, font="fa-med")
        s.line(x, 353, x + 48, 353, color=GRAY_C, lw=0.2, dash=[1.4, 1.4])
    s.fa("مشخصات فنی پس از تأیید نمونه‌های متریال تکمیل می‌شود.", 6.4, 276, 362,
         GRAPHITE, anchor="end", font="fa-light")
    s.en("NO PRODUCT NAMES, THICKNESSES OR CERTIFICATIONS ARE ASSERTED HERE", 5.0,
         24, 362, GRAPHITE, tracking=0.14)

    C.footer(s, 10, "متریال / برخورد بافت روشن و تیره")
    s.save()


# --------------------------------------------------------------------------- #
def s11(path, out_dir):
    s = D.Sheet(path, bg=PAPER_C)

    # ---- title ----
    s.fa("جزئیات، محل تلاقی فرم و اجرا", 20, 276, 30, INK, anchor="end")
    s.fa("خوانش دقیق لبه‌ها، سطوح و اتصالات قابل مشاهده", 8.8, 276, 41, INK_SOFT,
         anchor="end", font="fa-light")
    s.line(196, 47, 276, 47, color=GOLD, lw=0.45)
    s.en("DETAIL STUDY / FACADE INTERFACES", 5.8, 276, 55, GRAPHITE, anchor="end",
         tracking=0.2, font="en-med")

    # ---- main image: the genuine curved corner over the dark soffit ----
    C.image(s, "s11_main.jpg", 24, 78, 152, 90)
    rng = random.Random(43)
    s.pencil([(158, 96), (166, 112), (164, 130), (172, 146)], rng=rng, color=GRAPHITE,
             lw=0.3, jitter=0.3, passes=2, opacity=0.7)
    s.poly([(172, 146), (180, 152), (196, 160)], color=GOLD, lw=0.4, smooth=True)

    # ---- 01 : enlarged real CAD geometry of the curved frame ----
    s.fa("۰۱ — انحنای قاب روشن", 8.6, 276, 74, INK, anchor="end", font="fa-med")
    s.rect(196, 78, 80, 82, fill=PAPER_C, stroke=None)
    CD.draw_elevation(s, 198, 82, 26.0, y_from=17.0, y_to=18.85, x_from=7.05, x_to=10.80,
                      poche={"wall": PAPER_L, "shade": D.Color(0.93, 0.93, 0.91),
                             "glass": PAPER_C, "dark": D.Color(0.2, 0.2, 0.2)},
                      hatch=True,
                      weights={"heavy": (0.42, INK), "mid": (0.3, INK),
                               "thin": (0.2, INK_SOFT), "fine": (0.13, GRAPHITE)})
    s.line(198, 166, 274, 166, color=GOLD, lw=0.3)
    s.fa("بزرگ‌نمایی از هندسه واقعی نما", 5.2, 274, 170.5, GRAPHITE, anchor="end",
         font="fa-light")

    # ---- 02 : light band over the dark recess ----
    C.image(s, "s11_d2.jpg", 24, 190, 54, 36)
    s.fa("۰۲ — لبه پوسته و زیرسطح بالکن", 8.4, 82, 194, INK, font="fa-med")
    s.fa("سطوح قابل مشاهده از هندسه تأییدشده؛", 5.6, 82, 201, GRAPHITE, font="fa-light")
    s.fa("لایه‌های پنهان در این صفحه شماتیک هستند.", 5.6, 82, 207.6, GRAPHITE,
         font="fa-light")

    # ---- 03 : glazing, profile, solid parapet ----
    C.image(s, "s11_d3.jpg", 24, 240, 54, 34)
    s.fa("۰۳ — شیشه، پروفیل و لبه بالکن", 8.4, 82, 244, INK, font="fa-med")
    s.fa("جان‌پناه توپر و تقسیمات شیشه", 5.6, 82, 251, GRAPHITE, font="fa-light")
    s.fa("دست‌نخورده باقی مانده‌اند.", 5.6, 82, 257.6, GRAPHITE, font="fa-light")

    # ---- connective gold path: macro -> 01 -> 02/03 ----
    s.poly([(196, 160), (180, 176), (120, 196), (78, 206)], color=GOLD, lw=0.35,
           smooth=True, opacity=0.6)
    s.poly([(120, 196), (100, 226), (78, 254)], color=GOLD, lw=0.3, smooth=True,
           opacity=0.4)

    # ---- technical note ----
    s.line(24, 280, 276, 280, color=GRAY_W, lw=0.3)
    s.fa("جزئیات نهایی اتصالات و لایه‌های پنهان تابع مدارک اجرایی مصوب هستند.", 7.4,
         276, 290, INK_SOFT, anchor="end", font="fa-light")
    s.fa("هیچ اندازه، مهار یا لایه‌ای حدس زده نشده است.", 6.4, 276, 298, GRAPHITE,
         anchor="end", font="fa-light")

    # ---- locator: the three details on the real elevation ----
    CD.draw_elevation(s, 24, 306, 3.2, y_from=0, y_to=29.0, fills=False, hatch=False,
                      weights={"heavy": (0.16, GRAPHITE), "mid": (0.13, GRAPHITE),
                               "thin": (0.11, GRAPHITE), "fine": (0.09, GRAPHITE_L)})
    s.en("LOCATION OF THE THREE STUDIES", 4.6, 24, 302, GRAPHITE, tracking=0.12)
    for i, yy in enumerate([18.0, 13.0, 8.2]):
        yq = 306 + (29.0 - yy) * 3.2
        s.circle(24 + 10.8 * 3.2 + 3, yq, 1.0, fill=None, stroke=GOLD, lw=0.35)
        s.fa(C.fa_num(i + 1), 4.6, 24 + 10.8 * 3.2 + 3, yq + 1.1, GOLD,
             anchor="middle", font="fa-med")

    C.footer(s, 11, "جزئیات معماری")
    s.save()


# --------------------------------------------------------------------------- #
def s12(path, out_dir):
    s = D.Sheet(path, bg=PAPER_C)
    C.image(s, "s12_photo.jpg", 96, 0, 150, 24)
    s.line(96, 25.4, 246, 25.4, color=GOLD, lw=0.25)

    s.fa("خوانش لایه‌های پوسته", 21, 276, 40, INK, anchor="end")
    s.fa("از سطح نهایی تا رابطه اجزای معماری", 9.2, 276, 51, INK_SOFT, anchor="end",
         font="fa-light")
    s.line(198, 57, 276, 57, color=GOLD, lw=0.45)
    s.en("AXONOMETRIC / LAYERED READING OF THE SKIN", 5.8, 276, 65, GRAPHITE,
         anchor="end", tracking=0.18, font="en-med")

    # ---- three vertical strips: the same real elevation, read as three layers
    sc = 6.05
    w = 10.85 * sc
    y0 = 78
    h = 28.85 * sc
    xs = [24, 24 + w + 14, 24 + 2 * (w + 14)]
    base = dict(y_from=0.0, y_to=28.85, x_from=-0.05, x_to=10.80, clip=True,
                lw_scale=0.82)

    # 1 substrate (behind)
    CD.draw_elevation(s, xs[0], y0, sc, fills=False, hatch=False,
                      weights={"heavy": (0.18, D.Color(0.46, 0.46, 0.45)),
                               "mid": (0.15, D.Color(0.52, 0.52, 0.50)),
                               "thin": (0.11, D.Color(0.58, 0.58, 0.56)),
                               "fine": (0.08, D.Color(0.64, 0.64, 0.62))}, **base)
    s.rect(xs[0] - 2.6, y0 - 2.6, w + 5.2, h + 5.2, fill=None,
           stroke=D.Color(0.86, 0.86, 0.84), lw=0.2)

    # 2 recess + glazing
    CD.draw_elevation(s, xs[1], y0, sc, fills=True, hatch=False,
                      poche={"wall": D.Color(1, 1, 1), "shade": D.Color(0.905, 0.905, 0.895),
                             "glass": D.Color(0.760, 0.806, 0.836),
                             "dark": D.Color(0.180, 0.180, 0.176)},
                      kinds={"glass", "dark", "shade"},
                      weights={"heavy": (0.18, INK), "mid": (0.14, INK_SOFT),
                               "thin": (0.1, GRAPHITE), "fine": (0.08, GRAPHITE)}, **base)

    # 3 the outer ivory skin
    CD.draw_elevation(s, xs[2], y0, sc, fills=True, hatch=True,
                      poche={"wall": D.Color(0.928, 0.914, 0.884),
                             "shade": D.Color(0.836, 0.820, 0.790),
                             "glass": D.Color(1, 1, 1), "dark": D.Color(1, 1, 1)},
                      kinds={"wall", "shade"},
                      weights={"heavy": (0.2, INK), "mid": (0.15, INK_SOFT),
                               "thin": (0.11, GRAPHITE), "fine": (0.08, GRAPHITE)}, **base)

    # projection lines: the same four documented levels across all strips
    for lv in (24.20, 17.20, 10.10, 3.00):
        yy = y0 + (28.85 - lv) * sc
        s.line(xs[0] - 3, yy, xs[2] + w + 3, yy, color=GOLD, lw=0.18, dash=[1.2, 2.0],
               opacity=0.45)

    # layer captions under each strip
    caps = [(xs[0], ["۰۲ — بستر و زیرسازی", "۰۵ — ساختار پشتیبان"]),
            (xs[1], ["۰۳ — سطح زیرین بالکن", "۰۴ — سیستم شیشه و پروفیل"]),
            (xs[2], ["۰۱ — پوشش نهایی پوسته"])]
    for cx, lines in caps:
        s.line(cx, y0 + h + 3.6, cx + w, y0 + h + 3.6, color=GOLD, lw=0.3)
        for i, c in enumerate(lines):
            s.fa(c, 6.3, cx + w, y0 + h + 9 + i * 6.2, INK, anchor="end",
                 font="fa-light")

    # the structural substrate label
    s.line(24, y0 + h + 22.4, 33, y0 + h + 22.4, color=GOLD, lw=0.45)
    s.fa("زیرسازی سازه‌ای — مطابق نقشه مصوب", 6.0, 24, y0 + h + 27.4, GOLD,
         font="fa-light")

    # ---- closing register: two columns of notes -----------------------------
    s.line(24, 292, 276, 292, color=GRAY_W, lw=0.28)
    s.fa("ترتیب لایه‌ها از سمت راست به چپ: پوشش نهایی، سیستم شیشه و پروفیل، ساختار پشتیبان.",
         6.9, 276, 300, INK_SOFT, anchor="end", font="fa-light")
    s.fa("هر سه نوار از یک هندسه واقعی استخراج شده‌اند؛ تفاوت آن‌ها فقط تفکیک محتواست.",
         6.3, 276, 307.6, GRAPHITE, anchor="end", font="fa-light")
    s.fa("نمایش شماتیک روابط اجزا؛ اتصالات نهایی نیازمند تأیید اجرایی هستند.", 6.3,
         276, 315.2, GRAPHITE, anchor="end", font="fa-light")

    # ---- schematic section key: the five layers in one band (not to scale) ---
    ky, kh = 344, 15
    segs = [(58, "۰۱", "پوشش نهایی", D.Color(0.928, 0.914, 0.884)),
            (52, "۰۲", "بستر و زیرسازی", D.Color(0.880, 0.876, 0.864)),
            (44, "۰۳", "سطح زیرین بالکن", D.Color(0.235, 0.235, 0.230)),
            (40, "۰۴", "شیشه و پروفیل", D.Color(0.760, 0.806, 0.836)),
            (28, "۰۵", "ساختار پشتیبان", D.Color(0.640, 0.640, 0.620))]
    s.en("SCHEMATIC SECTION THROUGH THE SKIN — NOT TO SCALE", 4.4, 24, ky - 4,
         GRAPHITE, tracking=0.14)
    xx = 246.0
    for wseg, num, name, col in segs:
        s.rect(xx - wseg, ky, wseg, kh, fill=col, stroke=None)
        xx -= wseg
    xx = 246.0
    for wseg, num, name, col in segs:
        s.line(xx, ky - 1.6, xx, ky, color=INK, lw=0.2)
        s.line(xx - wseg, ky - 1.6, xx - wseg, ky, color=INK, lw=0.2)
        s.fa(num, 5.6, xx - wseg * 0.5, ky + kh + 6.4, INK, anchor="middle",
             font="fa-med")
        s.fa(name, 5.4, xx - wseg * 0.5, ky + kh + 12.6, GRAPHITE, anchor="middle",
             font="fa-light")
        xx -= wseg
    s.rect(24, ky, 222, kh, fill=None, stroke=None)

    note_lines = ["پوسته روشن شیاردار: سطح بیرونی پیوسته با انحنای نرم.",
                  "سطح تیره: زیرسطح بالکن‌ها با رگه‌های طبیعی.",
                  "شیشه و پروفیل: بازشوها با تقسیمات موجود.",
                  "پوشش گیاهی: کنترل‌شده و محدود به لبه بالکن‌ها."]
    s.fa("یادداشت متریال", 6.3, 150, 300, INK, anchor="end", font="fa-med")
    yy = 300
    for ln in note_lines:
        yy += 6.6
        s.fa(ln, 6.0, 150, yy, INK_SOFT, anchor="end", font="fa-light")

    C.footer(s, 12, "آکسونومتری / خوانش لایه‌ها")
    s.save()


# --------------------------------------------------------------------------- #
def s13(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)
    px, py, pw, ph = 44, 58, 176, 260

    # schematic urban masses: pale warm-gray, hand-drawn, clearly a placeholder
    rng = random.Random(51)
    ctx = D.Color(0.72, 0.72, 0.70)
    masses = [(22, 120, 20, 198, 6), (218, 100, 34, 150, 9), (218, 300, 48, 40, 5),
              (22, 340, 46, 50, 4), (250, 150, 26, 60, 7)]
    for (x, y, w, h, d) in masses:
        s.poly([(x, y + h), (x, y), (x + w, y), (x + w, y + h)], color=None,
               fill=D.Color(0.90, 0.895, 0.88), close=True, opacity=0.55)
        s.poly([(x, y), (x + d, y - d * 0.55), (x + w + d, y - d * 0.55), (x + w, y)],
               color=None, fill=D.Color(0.86, 0.855, 0.84), close=True, opacity=0.5)
        s.poly([(x + w, y), (x + w + d, y - d * 0.55), (x + w + d, y + h - d * 0.55),
                (x + w, y + h)], color=None, fill=D.Color(0.82, 0.815, 0.80), close=True,
               opacity=0.5)
        s.poly([(x, y + h), (x, y), (x + w, y), (x + w, y + h)], color=ctx, lw=0.35,
               opacity=0.5)
    s.en("SCHEMATIC CONTEXT — NOT A SURVEY", 4.6, 222, 92, GRAPHITE, tracking=0.14)

    # the photograph of the real building sits above the context drawing
    C.image(s, "s13_main.jpg", px, py, pw, ph)

    # roof silhouette trace, following the real termination of the building
    s.pencil([(56, 96), (72, 84), (92, 78), (120, 76), (150, 78), (172, 88),
              (186, 104)], rng=rng, color=GRAPHITE, lw=0.3, jitter=0.3,
             passes=2, opacity=0.55)
    s.poly([(186, 104), (200, 130), (214, 160), (224, 190)], color=GOLD, lw=0.4,
           smooth=True, opacity=0.85)
    for (xx, yy) in [(92, 78), (150, 78), (186, 104)]:
        s.circle(xx, yy, 1.0, fill=None, stroke=GOLD, lw=0.4)

    # ---- title ----
    s.en("URBAN CONTEXT / VISUAL INTEGRATION", 5.4, 44, 22, GRAPHITE, tracking=0.18,
         font="en-med")
    s.fa("نما در امتداد بافت شهری", 20, 44, 38, INK)
    s.fa("خوانایی حجم و تعادل در سیمای پیرامونی", 8.8, 44, 49, INK_SOFT, font="fa-light")
    s.line(44, 54, 200, 54, color=GOLD, lw=0.4)

    # ---- analysis labels ----
    s.fa("خوانش تحلیلی", 6.6, 276, 300, INK, anchor="end", font="fa-med")
    labels = ["خوانش سیلوئت", "تعادل میان سطوح روشن و تیره",
              "پیوستگی خطوط افقی و عمودی"]
    for i, lb in enumerate(labels):
        yy = 312 + i * 10
        C.marker(s, 26.2, yy - 1.0, C.fa_num(i + 1), r=2.0, fs=5.0)
        s.fa(lb, 7.0, 31, yy, INK, font="fa-light")
    s.fa("بافت پیرامونی — شماتیک", 6.8, 276, 360, GRAPHITE, anchor="end", font="fa-light")
    s.fa("تطبیق نهایی با برداشت وضع موجود و مدارک سایت انجام شود.", 6.4, 276, 368,
         INK_SOFT, anchor="end", font="fa-light")
    s.fa("حجم‌های پیرامونی صرفاً زمینه گرافیکی‌اند و ادعای نقشه برداشت ندارند.", 6.0,
         276, 376, GRAPHITE, anchor="end", font="fa-light")
    C.footer(s, 13, "بافت شهری؛ از بنا تا زمینه")
    s.save()


# --------------------------------------------------------------------------- #
STAGES = [
    ("۰۱", "برداشت وضع موجود و کنترل زیرکار"),
    ("۰۲", "تأیید نمونه متریال و ماکاپ"),
    ("۰۳", "آماده‌سازی زیرسازی و نقاط اتصال"),
    ("۰۴", "نصب و تنظیم پوسته و قاب‌ها"),
    ("۰۵", "اجرای شیشه، درزها و آب‌بندی"),
    ("۰۶", "کنترل نهایی، نظافت و تحویل"),
]


def s14(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)
    s.fa("از نقشه تا اجرای دقیق", 21, 276, 28, INK, anchor="end")
    s.fa("سناریوی اجرا، کنترل کیفیت و تحویل پوسته", 9.2, 276, 39, INK_SOFT,
         anchor="end", font="fa-light")
    s.line(198, 45, 276, 45, color=GOLD, lw=0.45)
    s.en("CONSTRUCTION SEQUENCE / QUALITY CONTROL", 5.6, 24, 28, GRAPHITE,
         tracking=0.2, font="en-med")

    # six stations on a 2 x 3 grid, joined by one continuous curved reading path
    cols = [24, 112, 200]
    rows = [88, 196]
    stations = []
    for r in range(2):
        order = range(3) if r == 0 else range(2, -1, -1)
        for c in order:
            stations.append((cols[c] + 6, rows[r]))

    # the path weaves behind the plates
    weaving = [(stations[0][0] - 16, stations[0][1] + 26)]
    for i, (x, y) in enumerate(stations):
        weaving.append((x + 34, y - 4))
    weaving.append((stations[-1][0] - 30, stations[-1][1] + 34))
    s.poly(weaving, color=GOLD, lw=0.45, smooth=True, opacity=0.45)
    s.pencil([(weaving[0][0] - 14, weaving[0][1] - 6), (weaving[0][0] - 6, weaving[0][1] - 2),
              weaving[0]], rng=random.Random(61), color=GRAPHITE, lw=0.35, jitter=0.3,
             passes=2, opacity=0.55)
    s.line(weaving[-1][0], weaving[-1][1], weaving[-1][0] - 16, weaving[-1][1] + 3,
           color=INK, lw=0.5)

    crops = ["s14_a.jpg", "s14_b.jpg", "s14_c.jpg", "s14_d.jpg"]
    for i, (num, cap) in enumerate(STAGES):
        x, y = stations[i]
        if i < 4:
            C.image(s, crops[i], x, y + 6, 62, 26)
            s.line(x, y + 3.2, x + 62, y + 3.2, color=GOLD, lw=0.22, opacity=0.8)
            cap_y = y + 42
        else:
            CD.draw_elevation(s, x, y + 8, 4.6, y_from=13.6, y_to=18.2,
                              x_from=4.0, x_to=10.6, fills=False, hatch=False,
                              weights={"heavy": (0.24, INK), "mid": (0.16, INK),
                                       "thin": (0.12, INK_SOFT), "fine": (0.09, GRAPHITE)})
            cap_y = y + 42
        C.marker(s, x - 4.5, y + 4, num[1], r=2.3, fs=5.2)
        s.fa(f"{num} — {cap}", 6.6, x + 58, cap_y, INK, anchor="end", font="fa-light")

    # quality-control strip
    s.line(24, 286, 276, 286, color=GRAY_W, lw=0.3)
    s.fa("نوار کنترل کیفیت", 7.4, 276, 294, INK_SOFT, anchor="end", font="fa-med")
    checks = ["کنترل هندسه و تراز", "کنترل اتصالات و ایمنی",
              "کنترل آب‌بندی و زهکشی", "کنترل کیفیت سطح و نظافت"]
    for i, txt in enumerate(checks):
        x = 24 + i * 63
        s.rect(x, 300, 3.4, 3.4, fill=None, stroke=GOLD, lw=0.35)
        s.fa(txt, 6.6, x + 5.6, 304, INK_SOFT, font="fa-light")
        s.line(x, 310, x + 52, 310, color=GRAY_W, lw=0.2)

    s.fa("ترتیب عملیات، روش نصب و نقاط بازرسی باید در برنامه اجرایی مصوب پروژه تعیین شوند.",
         7.0, 276, 330, INK_SOFT, anchor="end", font="fa-light")
    s.fa("هیچ تاریخ، مدت‌زمان یا نتیجه بازرسی‌ای در این صفحه ادعا نشده است.", 6.2, 276,
         338, GRAPHITE, anchor="end", font="fa-light")
    C.footer(s, 14, "از نقشه تا اجرا")
    s.save()


# --------------------------------------------------------------------------- #
def s15(path, out_dir):
    s = D.Sheet(path, bg=PAPER_L)
    C.image(s, "s15_crop.jpg", 0, 0, 297, 170)

    # faint elevation fragment beneath the photograph, dissolving into paper
    CD.draw_elevation(s, 168, 322, 3.0, y_from=19.5, y_to=28.9, fills=False,
                      hatch=False,
                      weights={"heavy": (0.18, GRAPHITE_L), "mid": (0.14, GRAPHITE_L),
                               "thin": (0.1, GRAPHITE_L), "fine": (0.08, GRAPHITE_L)})

    # signature line: real curved edge -> gold line -> precise horizontal stroke
    rng = random.Random(71)
    s.pencil([(112, 176), (96, 188), (84, 202), (78, 218)], rng=rng, color=GRAPHITE,
             lw=0.34, jitter=0.35, passes=2, opacity=0.65)
    s.poly([(78, 218), (70, 252), (52, 300), (30, 352), (24, 366), (24, 378)],
           color=GOLD, lw=0.6, smooth=True)
    s.line(24, 378, 148, 378, color=GOLD, lw=0.6)
    s.circle(148, 378, 0.7, fill=GOLD)

    # closing statement, lower left quadrant
    x = 132
    s.fa("از ایده تا جزئیات،", 17, x, 236, INK)
    s.fa("از فرم تا عملکرد،", 17, x, 251, INK)
    s.fa("یک پوسته با هویت مشخص.", 17, x, 266, INK)
    s.fa("دفترچه طراحی پوسته و نمای ساختمان", 8.4, x, 288, INK_SOFT, font="fa-light")
    s.fa("مجموعه ارائه معماری و مستندات فنی", 8.4, x, 298, GRAPHITE, font="fa-light")
    s.en("FACADE DESIGN", 6.4, 24, 288, GRAPHITE, tracking=0.22, font="en-med")
    s.en("DESIGN INTENT / TECHNICAL DEVELOPMENT", 5.6, 24, 296, GRAPHITE, tracking=0.18)

    s.fa("آپارتمان مسکونی رمضانی — بابلسر، مازندران", 6.2, 24, 410, GRAPHITE,
         font="fa-light")
    s.en("15 — 15", 5.6, 276, 410, GRAPHITE, anchor="end", tracking=0.16)
    s.save()
