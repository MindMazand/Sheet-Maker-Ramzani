"""Builds every photographic plate at exactly the size it occupies on paper."""
from __future__ import annotations

import os

from PIL import Image, ImageEnhance, ImageFilter

import plates
from plates import Master, night_plate

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
os.makedirs(A, exist_ok=True)


def build(m=None):
    m = m or Master()
    # ---------------------------------------------------------------- covers
    m.crop((0.00, 0.00, 1.00, 1.00), 197, 251, f"{A}/s01_hero.jpg",
           ref="ivory", clarity=0.22, sat=1.03, sharp=1.22, contrast=1.02)
    # small detail crop for the cover (curved corner + soffit)
    m.crop((0.44, 0.44, 0.63, 0.60), 54, 44, f"{A}/s01_detail.jpg",
           ref="ivory", clarity=0.3, sat=1.02, sharp=1.3)

    # ------------------------------------------------------------ sheet 02
    m.crop((0.28, 0.06, 0.90, 0.94), 168, 235, f"{A}/s02_facade.jpg",
           ref="ivory", clarity=0.2, sat=1.02, sharp=1.2)
    m.crop((0.30, 0.30, 0.56, 0.50), 52, 40, f"{A}/s02_frag1.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)
    m.crop((0.52, 0.62, 0.78, 0.80), 52, 36, f"{A}/s02_frag2.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)

    # ------------------------------------------------------------ sheet 03
    m.crop((0.36, 0.34, 0.76, 0.66), 190, 150, f"{A}/s03_macro.jpg",
           ref="ivory", clarity=0.30, sat=1.02, sharp=1.35)
    m.crop((0.28, 0.40, 0.66, 0.47), 232, 34, f"{A}/s03_soffit.jpg",
           ref="ivory", clarity=0.35, sharp=1.3)

    # ------------------------------------------------------------ sheet 04
    m.crop((0.02, 0.005, 0.985, 0.995), 261, 344, f"{A}/s04_day.jpg",
           ref="ivory", clarity=0.26, sat=1.06, sharp=1.3, contrast=1.03)
    m.crop((0.46, 0.09, 0.73, 0.21), 68, 32, f"{A}/s04_corner.jpg",
           ref="ivory", clarity=0.3, sharp=1.3)

    # ------------------------------------------------------------ sheet 05
    night_plate(m, (0.02, 0.0, 0.93, 0.97), 282, 356, f"{A}/s05_night.jpg",
                exposure=1.05, ambient=0.30, context=0.045)
    m.crop((0.33, 0.35, 0.60, 0.47), 56, 26, f"{A}/s05_day_crop.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)

    # ------------------------------------------------------------ sheet 06
    m.crop((0.27, 0.30, 0.62, 0.92), 34, 262, f"{A}/s06_strip.jpg",
           ref="ivory", clarity=0.2, sharp=1.2)

    # ------------------------------------------------------------ sheet 07
    m.crop((0.30, 0.06, 0.80, 0.30), 66, 56, f"{A}/s07_detail.jpg",
           ref="ivory", clarity=0.28, sharp=1.3)

    # ------------------------------------------------------------ sheet 08
    m.crop((0.20, 0.36, 0.42, 0.55), 52, 62, f"{A}/s08_corner.jpg",
           ref="ivory", clarity=0.3, sharp=1.3)

    # ------------------------------------------------------------ sheet 09
    m.crop((0.28, 0.78, 0.86, 0.99), 150, 30, f"{A}/s09_base.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)

    # ------------------------------------------------------------ sheet 10
    m.crop((0.30, 0.10, 0.86, 0.56), 152, 128, f"{A}/s10_main.jpg",
           ref="ivory", clarity=0.25, sat=1.02, sharp=1.25)
    m.crop((0.28, 0.44, 0.40, 0.86), 31, 118, f"{A}/s10_rib.jpg",
           ref="ivory", clarity=0.55, sat=1.0, sharp=1.45)
    m.crop((0.30, 0.415, 0.72, 0.455), 174, 26, f"{A}/s10_soffit.jpg",
           ref="ivory", clarity=0.5, sat=1.0, sharp=1.4)
    m.crop((0.53, 0.60, 0.70, 0.72), 56, 40, f"{A}/s10_glass.jpg",
           ref="neutral", clarity=0.3, sharp=1.3)

    # ------------------------------------------------------------ sheet 11
    m.crop((0.30, 0.44, 0.62, 0.66), 156, 92, f"{A}/s11_main.jpg",
           ref="ivory", clarity=0.3, sharp=1.3)
    m.crop((0.52, 0.30, 0.68, 0.40), 54, 34, f"{A}/s11_d3.jpg",
           ref="ivory", clarity=0.35, sharp=1.35)
    m.crop((0.31, 0.42, 0.44, 0.50), 44, 30, f"{A}/s11_d2.jpg",
           ref="ivory", clarity=0.35, sharp=1.35)

    # ------------------------------------------------------------ sheet 12
    m.crop((0.34, 0.07, 0.78, 0.21), 96, 30, f"{A}/s12_photo.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)

    # ------------------------------------------------------------ sheet 13
    m.crop((0.18, 0.055, 0.95, 0.99), 176, 264, f"{A}/s13_main.jpg",
           ref="ivory", clarity=0.18, sat=1.0, sharp=1.18)

    # ------------------------------------------------------------ sheet 14
    m.crop((0.30, 0.06, 0.72, 0.20), 62, 28, f"{A}/s14_a.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)
    m.crop((0.28, 0.33, 0.72, 0.45), 62, 24, f"{A}/s14_b.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)
    m.crop((0.53, 0.48, 0.85, 0.60), 62, 24, f"{A}/s14_c.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)
    m.crop((0.31, 0.62, 0.75, 0.74), 62, 24, f"{A}/s14_d.jpg",
           ref="ivory", clarity=0.25, sharp=1.25)

    # ------------------------------------------------------------ sheet 15
    m.crop((0.30, 0.30, 0.86, 0.62), 246, 140, f"{A}/s15_crop.jpg",
           ref="ivory", clarity=0.22, sat=1.02, sharp=1.22)


if __name__ == "__main__":
    build()
    print("plates built")
