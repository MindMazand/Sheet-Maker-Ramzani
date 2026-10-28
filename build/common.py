"""Shared editorial furniture and helpers."""
from __future__ import annotations

import os

import lib_text as T
from design import (GOLD, GOLD_L, GOLD_PALE, GRAPHITE, GRAPHITE_L, GRAY_W, INK,
                    INK_SOFT, MM, PAPER, PAPER_C, PAPER_L, WHITE)

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")

FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def fa_num(n, pad=2):
    s = f"{n}".zfill(pad)
    return "".join(FA_DIGITS[int(c)] if c.isdigit() else c for c in s)


def fa_digits(s):
    return "".join(FA_DIGITS[int(c)] if c.isdigit() else c for c in s)


def series_head(s, color=GRAPHITE, right=276, y=18, label=None):
    """Running head: thin gold rule + Persian series line + English microtype."""
    s.line(right - 62, y, right, y, color=GOLD, lw=0.4)
    s.fa(label or "دفترچه طراحی پوسته و نمای ساختمان", 6.6, right, y - 2.6, color,
         anchor="end", font="fa-light")


def footer(s, n, label_fa, dark=False, total=15, y=406, color=None, gold=GOLD):
    col = color or (GRAPHITE_L if dark else GRAPHITE)
    s.line(21, y - 3.2, 276, y - 3.2, color=gold if dark else GRAY_W, lw=0.25,
           opacity=0.85)
    s.fa(f"شیت {fa_num(n)}", 7.0, 21, y + 2.2, col, font="fa-med")
    s.en(f"{n:02d} — {total:02d}", 6.4, 21, y + 6.4, col, tracking=0.16, font="en-med")
    s.fa(label_fa, 7.0, 276, y + 2.2, col, anchor="end", font="fa-light")


def english_micro(s, text, x, y, color=GRAPHITE, size=6.4, tracking=0.2, anchor="start"):
    s.en(text, size, x, y, color, anchor=anchor, tracking=tracking, font="en-med")


def caption_pair(s, fa_txt, en_txt, x, y, color=INK_SOFT, anchor="start",
                 fa_size=7.4, en_size=6.0, gap=4.4):
    if fa_txt:
        s.fa(fa_txt, fa_size, x, y, color, anchor=anchor, font="fa-light")
    if en_txt:
        s.en(en_txt, en_size, x, y + gap, GRAPHITE, anchor=anchor, tracking=0.18,
             font="en-med")


def marker(s, x, y, num_fa, color=GOLD, ink=None, r=2.4, fs=5.6, ring=True):
    """Small numbered editorial marker (not construction geometry)."""
    if ring:
        s.circle(x, y, r, fill=None, stroke=color, lw=0.4)
    s.fa(num_fa, fs, x, y + fs / MM * 0.36, ink or color, anchor="middle", font="fa-med")


def leader(s, pts, color=GRAPHITE, lw=0.2, dash=None, dot=True, opacity=None):
    """Thin callout leader that ends with a small dot at the last point."""
    s.poly(pts, color=color, lw=lw, dash=dash, opacity=opacity, cap=1)
    if dot:
        s.circle(pts[-1][0], pts[-1][1], 0.42, fill=color, opacity=opacity)


def rule_with_caps(s, x1, x2, y, color=GOLD, lw=0.5, caps=True, cap_len=1.6):
    s.line(x1, y, x2, y, color=color, lw=lw)
    if caps:
        s.line(x1, y - cap_len, x1, y + cap_len, color=color, lw=lw)
        s.line(x2, y - cap_len, x2, y + cap_len, color=color, lw=lw)


def soft_shadow(s, x, y, w, h, spread=4, opacity=0.06, steps=7):
    """Very soft drop shadow used sparingly under hero plates."""
    for i in range(steps, 0, -1):
        f = i / steps
        s.rect(x - spread * f, y - spread * f, w + 2 * spread * f, h + 2 * spread * f,
               fill=INK, stroke=None, opacity=opacity * (1 - f) * 0.5 + 0.004)


def image(s, name, x, y, w, h, **kw):
    s.image(os.path.join(A, name), x, y, w, h, **kw)


def tick_ruler(s, x, y, w, n=10, color=GRAPHITE_L, lw=0.18, h=1.2):
    s.line(x, y, x + w, y, color=color, lw=lw)
    for i in range(n + 1):
        xx = x + w * i / n
        s.line(xx, y - (h if i % 5 else h * 1.8), xx, y, color=color, lw=lw)
