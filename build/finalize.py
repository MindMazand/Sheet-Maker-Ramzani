"""Finalize: 300 dpi JPEGs, a single combined PDF, and a contact sheet."""
from __future__ import annotations

import glob
import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "sheets")


def main():
    pdfs = sorted(glob.glob(os.path.join(OUT, "s??.pdf")))
    assert len(pdfs) == 15, len(pdfs)
    merged = pymupdf.open()
    for p in pdfs:
        d = pymupdf.open(p)
        merged.insert_pdf(d)
        # 300 dpi JPEG companion
        base = os.path.splitext(p)[0]
        pix = d[0].get_pixmap(dpi=300)
        pix.save(base + ".jpg", jpg_quality=94)
    merged.set_metadata({})
    merged.save(os.path.join(OUT, "00_facade_monograph_A3.pdf"), deflate=True)
    print("merged", len(merged), "pages")

    # contact sheet of all 15 (for quick review, not a deliverable)
    thumbs = []
    for p in pdfs:
        d = pymupdf.open(p)
        pix = d[0].get_pixmap(dpi=40)
        thumbs.append(pymupdf.Pixmap(pix))
    cols, rows = 5, 3
    w, h = thumbs[0].width, thumbs[0].height
    sheet = pymupdf.open()
    page = sheet.new_page(width=w * cols + 20 * (cols + 1), height=h * rows + 20 * (rows + 1))
    for i, pix in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = 20 + c * (w + 20)
        y = 20 + r * (h + 20)
        page.insert_image(pymupdf.Rect(x, y, x + w, y + h), pixmap=pix)
    page.get_pixmap(dpi=110).save(os.path.join(HERE, "tmp", "contact.png"))
    print("contact sheet done")


if __name__ == "__main__":
    main()
