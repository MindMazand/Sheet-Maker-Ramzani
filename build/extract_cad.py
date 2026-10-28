"""Extract a metric model of the facade elevation from My_PDF.pdf (vector CAD).

The PDF pages are A4 reductions of the original CAD sheet. Empirically the
drawing is quantised at exactly 20.0 pt per metre (verified against the
+28.85 level and the 10.50 m overall width), which lets every vector
coordinate be converted into true metres before it is redrawn.

Outputs build/data/cad.json
"""
from __future__ import annotations

import json
import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "My_PDF.pdf")

PT_PER_M = 20.0
P3_ORIGIN = (264.0, 700.2)   # page 3: x of left facade edge, y of +0.00
P2_ORIGIN = (240.0, 700.2)


def to_m(rect, origin):
    x0, y0, x1, y1 = rect
    return [
        round((x0 - origin[0]) / PT_PER_M, 4),
        round((origin[1] - y1) / PT_PER_M, 4),   # bottom, in metres above 0.00
        round((x1 - x0) / PT_PER_M, 4),
        round((y1 - y0) / PT_PER_M, 4),
    ]


def main():
    doc = pymupdf.open(PDF)
    out = {"pt_per_m": PT_PER_M}

    # ---------------- page 3 : the styled elevation (geometry authority) ----
    p3 = doc[2]
    fills, lines = [], []
    for it in p3.get_drawings():
        r = it["rect"]
        f = it["fill"]
        c = it["color"]
        if f is not None and f != (1.0, 1.0, 1.0):
            kind = "wall"
            if f[2] > 0.9 and f[0] < 0.75:
                kind = "glass"
            elif sum(f) < 0.1:
                kind = "dark"
            elif f[0] < 0.7:
                kind = "shade"
            m = to_m((r.x0, r.y0, r.x1, r.y1), P3_ORIGIN)
            fills.append({"k": kind, "r": m,
                          "sub": it["items"][0][0] if it["items"] else None,
                          "pt": r.height})
        elif c is not None:
            m = to_m((r.x0, r.y0, r.x1, r.y1), P3_ORIGIN)
            if r.width > 0.05 or r.height > 0.05:
                lines.append({"r": m, "w": it["width"] or 0.1,
                              "horiz": r.height < r.width})
    out["elev_fills"] = fills
    out["elev_lines"] = lines

    # ---------------- page 2 : dimensions + levels ---------------------------
    p2 = doc[1]
    words = []
    d = p2.get_text("dict")
    for b in d["blocks"]:
        for l in b.get("lines", []):
            dirv = l.get("dir", (1, 0))
            for s in l["spans"]:
                txt = s["text"].strip()
                if not txt:
                    continue
                x0, y0, x1, y1 = s["bbox"]
                words.append({
                    "t": txt,
                    "x": round(((x0 + x1) / 2 - P2_ORIGIN[0]) / PT_PER_M, 3),
                    "y": round((P2_ORIGIN[1] - (y0 + y1) / 2) / PT_PER_M, 3),
                    "w": round((x1 - x0) / PT_PER_M, 3),
                    "h": round((y1 - y0) / PT_PER_M, 3),
                    "rot": 90 if abs(dirv[1]) > 0.5 else 0,
                    "size": round(s["size"] / PT_PER_M * 72 / 72, 3),
                })
    out["dims"] = words

    # dimension line-work on page 2 (thin strokes only)
    dimlines = []
    for it in p2.get_drawings():
        r = it["rect"]
        if it["fill"] is not None or it["color"] is None:
            continue
        if (it["width"] or 1) > 0.45:
            continue
        m = to_m((r.x0, r.y0, r.x1, r.y1), P2_ORIGIN)
        if r.width > 3 or r.height > 3:
            dimlines.append({"r": m, "w": it["width"], "horiz": r.height < r.width})
    out["dim_lines"] = dimlines

    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    with open(os.path.join(HERE, "data", "cad.json"), "w") as fh:
        json.dump(out, fh)
    print("fills", len(fills), "lines", len(lines), "words", len(words), "dimlines", len(dimlines))


if __name__ == "__main__":
    main()
