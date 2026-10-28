"""Full vector extraction of the CAD elevation (page 3 of My_PDF.pdf).

Strokes are kept as polylines (beziers sampled), fills as polygons, all in
metres in elevation space: x from the left facade edge, y from +0.00.
Nothing is reconstructed: the sheet later re-colours and re-weights the real
CAD linework.
"""
from __future__ import annotations

import json
import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "My_PDF.pdf")

PT_PER_M = 20.0
ORIGIN = (264.0, 700.2)   # page-3 point of (x=0 m, y=0.00)


def m_x(x):
    return (x - ORIGIN[0]) / PT_PER_M


def m_y(y):
    return (ORIGIN[1] - y) / PT_PER_M


def sample_cubic(p0, p1, p2, p3, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        out.append((x, y))
    return out


def classify(fill):
    if fill is None:
        return None
    if fill[2] > 0.9 and fill[0] < 0.75:
        return "glass"
    if sum(fill) < 0.12:
        return "dark"
    if fill[0] < 0.70:
        return "shade"
    return "wall"


def main():
    doc = pymupdf.open(PDF)
    page = doc[2]
    fills, strokes = [], []
    for it in page.get_drawings():
        kind = classify(it["fill"])
        col = it["color"]
        w = it["width"]
        for item in it["items"]:
            op = item[0]
            if op == "re":
                r = item[1]
                pts = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
            elif op == "qu":
                q = item[1]
                pts = [tuple(q.ul), tuple(q.ur), tuple(q.lr), tuple(q.ll)]
            elif op == "l":
                pts = [tuple(item[1]), tuple(item[2])]
            elif op == "c":
                pts = [tuple(item[1])] + sample_cubic(tuple(item[1]), tuple(item[2]),
                                                      tuple(item[3]), tuple(item[4]))
            else:
                continue
            mp = [(round(m_x(x), 3), round(m_y(y), 3)) for x, y in pts]
            xs = [p[0] for p in mp]
            ys = [p[1] for p in mp]
            if max(xs) < -1.6 or min(xs) > 12.2 or max(ys) < -0.4 or min(ys) > 30.4:
                continue
            if kind is None:
                span = max(max(xs) - min(xs), max(ys) - min(ys))
                if span > 40:      # sheet border / ground line
                    continue
                if (w or 0) > 2.0:
                    continue
                plen = sum(((mp[i + 1][0] - mp[i][0]) ** 2 + (mp[i + 1][1] - mp[i][1]) ** 2) ** 0.5
                           for i in range(len(mp) - 1))
                if plen > 22:
                    continue
            if kind is not None:
                fills.append({"k": kind, "p": mp})
            elif col is not None:
                strokes.append({"w": round(w or 0.1, 2),
                                "s": (1 if col[0] < 0.6 else 0),
                                "p": mp})
    # dedupe exact repeats (the PDF draws some entities twice)
    seen = set()
    uf, us = [], []
    for f in fills:
        key = (f["k"], tuple((round(x, 2), round(y, 2)) for x, y in f["p"]))
        if key in seen:
            continue
        seen.add(key)
        uf.append(f)
    seen = set()
    for s in strokes:
        key = (s["w"], tuple((round(x, 2), round(y, 2)) for x, y in s["p"]))
        if key in seen:
            continue
        seen.add(key)
        us.append(s)

    out = {"fills": uf, "strokes": us}
    with open(os.path.join(HERE, "data", "cad_elev.json"), "w") as fh:
        json.dump(out, fh)
    print("fills", len(uf), "strokes", len(us))


if __name__ == "__main__":
    main()
