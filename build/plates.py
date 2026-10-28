"""Image plate factory.

Rules of engagement
-------------------
* The architectural geometry is never touched: crops, tone, contrast, colour
  temperature and sharpening only. No warping, no in-painting of the building,
  no generative re-imagining of the facade.
* Every plate is written at exactly 300 DPI for the millimetre size it will
  occupy on the sheet, so nothing is resampled by the PDF writer.

Night plate (sheet 05)
----------------------
The dusk plate is a *relight* of the master photograph: linear-light exposure
compression, sky replacement, emissive recovery of the warm luminaires that
already exist in the render, and interior light behind the existing glazing.
Geometry (silhouette, floor lines, parapets, glazing divisions) is identical by
construction, because it is the same pixels.
"""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "assets")
MASTER = os.path.join(ROOT, "blank.png")

DPI = 300.0


class Master:
    def __init__(self, path=MASTER, upscale=1.45):
        im = Image.open(path).convert("RGB")
        if upscale != 1.0:  # pre-press upscale so hero plates stay >=250 dpi
            im = im.resize((int(im.width * upscale), int(im.height * upscale)), Image.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=2.2, percent=45, threshold=2))
        self.im = im
        self.w, self.h = im.size
        self.arr = np.asarray(im, dtype=np.float32) / 255.0

    # ---------------------------------------------------------------- helpers
    def box(self, x0, y0, x1, y1):
        """Relative box (0..1 in the master frame) -> pixel box."""
        return (int(x0 * self.w), int(y0 * self.h), int(x1 * self.w), int(y1 * self.h))

    def crop(self, rel, out_w_mm, out_h_mm, path, ref="ivory", clarity=1.0,
             sat=1.0, sharp=1.3, contrast=1.0, brightness=1.0, desat_shadow=0.0,
             tmp=None, upscale_to_dpi=True):
        box = self.box(*rel) if max(rel) <= 1.0 else tuple(int(v) for v in rel)
        im = self.im.crop(box)
        src = np.asarray(im, dtype=np.float32) / 255.0
        if ref == "ivory":
            src = _white_balance(src, target=(0.94, 0.925, 0.895))
        elif ref == "neutral":
            src = _white_balance(src, target=(0.95, 0.95, 0.95))
        if desat_shadow:
            src = _shadow_desat(src, desat_shadow)
        arr = np.clip(src, 0, 1)
        if contrast != 1.0:
            arr = np.clip((arr - 0.5) * contrast + 0.5, 0, 1)
        if brightness != 1.0:
            arr = np.clip(arr * brightness, 0, 1)
        im = Image.fromarray((arr * 255).astype(np.uint8))
        if sat != 1.0:
            im = ImageEnhance.Color(im).enhance(sat)
        if clarity != 1.0:
            blur = im.filter(ImageFilter.GaussianBlur(6))
            im = Image.fromarray(np.clip(
                np.asarray(im, np.float32) + clarity * (np.asarray(im, np.float32) - np.asarray(blur, np.float32)),
                0, 255).astype(np.uint8))
        if sharp > 1.0:
            im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=int((sharp - 1) * 130), threshold=2))
        if upscale_to_dpi:
            tw = int(round(out_w_mm / 25.4 * DPI))
            th = int(round(out_h_mm / 25.4 * DPI))
            # cover-fit, never distort
            sc = max(tw / im.width, th / im.height)
            im = im.resize((max(tw, int(im.width * sc)), max(th, int(im.height * sc))), Image.LANCZOS)
            left = (im.width - tw) // 2
            top = (im.height - th) // 2
            im = im.crop((left, top, left + tw, top + th))
        im.save(path, quality=96, subsampling=1, dpi=(DPI, DPI))
        return path


def _white_balance(arr, target):
    """Map the facade's ivory body to a fixed neutral-warm point (grey-world on
    a high-percentile sample of the bright facade pixels)."""
    lum = arr.mean(axis=2)
    mask = (lum > np.percentile(lum, 78)) & (lum < np.percentile(lum, 99.2))
    if mask.sum() < 100:
        return arr
    cur = np.array([arr[..., i][mask].mean() for i in range(3)], dtype=np.float32)
    cur = np.maximum(cur, 1e-3)
    gain = np.array(target, dtype=np.float32) / cur
    gain = gain / gain[1]
    gain = np.clip(gain, 0.93, 1.09)
    return np.clip(arr * gain, 0, 1)


def _shadow_desat(arr, amount):
    lum = arr.mean(axis=2)[..., None]
    weight = np.clip(1.0 - lum * 2.0, 0, 1) * amount
    flat = np.repeat(lum, 3, axis=2)
    return arr * (1 - weight) + flat * weight


# --------------------------------------------------------------------------- #
# night relight
# --------------------------------------------------------------------------- #
# silhouette of the featured block in the master photograph (relative coords).
# Used only to separate the subject from its context when relighting at dusk -
# it never alters any pixel geometry.
TOWER = [(0.335, 0.093), (0.700, 0.075), (0.730, 0.120), (0.745, 0.300),
         (0.790, 0.520), (0.815, 0.700), (0.845, 0.960), (0.320, 1.000),
         (0.300, 0.860), (0.250, 0.700), (0.225, 0.560), (0.245, 0.400),
         (0.275, 0.240), (0.310, 0.150)]


def _poly_mask(size, pts_rel, feather=12):
    from PIL import ImageDraw
    w, h = size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x * w, y * h) for x, y in pts_rel], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m, np.float32) / 255.0


def night_plate(master: Master, rel, out_w_mm, out_h_mm, path, exposure=1.0,
                ambient=0.30, context=0.05):
    """Blue-hour relight of the master render; geometry untouched."""
    box = master.box(*rel)
    im = master.im.crop(box)
    arr = np.asarray(im, np.float32) / 255.0
    h, w, _ = arr.shape

    # ---------- masks at half resolution ----------------------------------
    small = np.asarray(im.resize((w // 2, h // 2), Image.BILINEAR), np.float32) / 255.0
    hs, ws, _ = small.shape
    lum_s = small.mean(axis=2)
    blueness = small[..., 2] - small[..., 0]
    skyish = (blueness > 0.012) & (lum_s > 0.22)
    skyish = ndimage.binary_opening(skyish, np.ones((5, 5)))
    lab, n = ndimage.label(skyish)
    keep = np.zeros_like(skyish)
    for i in range(1, n + 1):
        ys = np.where(lab == i)[0]
        if len(ys) < 700 or ys.min() > hs * 0.10:
            continue
        keep |= (lab == i)
    keep = ndimage.binary_closing(keep, np.ones((9, 9)))
    sky_s = ndimage.gaussian_filter(keep.astype(np.float32), 5)
    sky_s = np.clip((sky_s - 0.2) / 0.6, 0, 1)
    sky = np.asarray(Image.fromarray((sky_s * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                     np.float32) / 255.0
    sky = sky[..., None]

    # subject envelope in *master* coordinates
    tw = _poly_mask((w, h), [( (x - rel[0]) / (rel[2] - rel[0]),
                               (y - rel[1]) / (rel[3] - rel[1])) for x, y in TOWER],
                    feather=9)
    subject = (1 - sky[..., 0]) * tw

    # ---------- blue-hour sky ---------------------------------------------
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    cloud = ndimage.gaussian_filter(lum_s, 7)
    cloud = (cloud - cloud.min()) / (np.ptp(cloud) + 1e-6)
    cloud = np.asarray(Image.fromarray((cloud * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                       np.float32) / 255.0
    relief = 0.88 + 0.26 * ndimage.gaussian_filter(cloud, 4)
    top = np.array([0.055, 0.098, 0.180], np.float32)
    mid = np.array([0.098, 0.145, 0.231], np.float32)
    hor = np.array([0.243, 0.259, 0.302], np.float32)
    t = yy[..., None]
    grad = np.where(t < 0.60, top + (mid - top) * (t / 0.60), mid + (hor - mid) * ((t - 0.60) / 0.40))
    newsky = np.clip(grad * relief[..., None], 0, 1)
    band = np.exp(-((yy - 0.50) ** 2) / 0.045)[..., None] * np.array([0.085, 0.045, 0.010], np.float32)
    newsky = np.clip(newsky + band, 0, 1)

    # ---------- dusk ambient on the architecture ---------------------------
    lin = _srgb_to_lin(arr)
    lum = arr.mean(axis=2)
    cool = np.array([0.74, 0.77, 0.86], np.float32)
    # keep the daylight modelling (it *is* the real geometry), just drop exposure
    model = np.clip(lin ** 1.16, 0, 1) * cool * ambient
    model = model * (0.55 + 0.45 * subject[..., None])
    ctx = np.clip(lin ** 1.1, 0, 1) * np.array([0.70, 0.76, 0.88], np.float32) * context
    # attenuate high-frequency detail at low ambient light: keeps the large-scale
    # modelling of the real geometry, removes sensor-scale mottling
    smooth = ndimage.gaussian_filter(model, (5, 5, 0))
    model = smooth + (model - smooth) * 0.42
    body = model * subject[..., None] + ctx * (1 - subject[..., None])

    # ---------- emissive: the warm sources that already exist ---------------
    warmness = arr[..., 0] - np.maximum(arr[..., 1], arr[..., 2])
    src = np.clip((warmness - 0.035) * 10.0, 0, 1) * np.clip((lum - 0.30) * 2.4, 0, 1)
    src = src * subject
    core = ndimage.gaussian_filter(src, 1.2)
    halo = ndimage.gaussian_filter(src, 7.5)
    mid_ = ndimage.gaussian_filter(src, 3.0)
    glow = (core * 1.25 + mid_ * 0.85 + halo * 0.55)[..., None] * np.array([1.0, 0.70, 0.40], np.float32)
    body = body + glow * 1.25

    # warm spill from the recessed downlights onto the nearby shell surfaces
    spill = ndimage.gaussian_filter(src, 26)
    spill = spill / (spill.max() + 1e-6)
    body = body + (spill * 0.55 * (0.35 + 0.65 * lum))[..., None] * np.array([0.42, 0.24, 0.09], np.float32)
    # cool sky bounce on upward-facing soffits and parapet tops
    body = body + (np.clip(lum - 0.35, 0, 1) * subject * 0.10)[..., None] * np.array([0.10, 0.14, 0.22], np.float32)

    # ---------- blend sky / architecture -----------------------------------
    out_lin = body * (1 - sky) + _srgb_to_lin(newsky) * sky
    out_lin = _tonemap(out_lin, exposure)
    out = np.clip(_lin_to_srgb(out_lin), 0, 1)
    # midnight grade: protect highlights, deepen the toe a little
    out = np.clip(out ** 1.02, 0, 1)
    im2 = Image.fromarray((out * 255).astype(np.uint8))
    # silhouette-preserving smoothing tames sensor-scale rib noise without
    # touching large-scale form (essential for a believable night plate)
    sm = np.asarray(im2.filter(ImageFilter.GaussianBlur(2.4)), np.float32)
    sh = np.asarray(im2, np.float32)
    edge = np.clip((np.abs(ndimage.gaussian_filter(sh.mean(axis=2), 1.4) -
                           ndimage.gaussian_filter(sh.mean(axis=2), 4.0))) / 14.0, 0, 1)[..., None]
    im2 = Image.fromarray(np.clip(sm * (1 - 0.55 * edge) + sh * (0.55 * edge), 0, 255).astype(np.uint8))
    im2 = _fit(im2, out_w_mm, out_h_mm)
    im2.save(path, quality=95, subsampling=1, dpi=(DPI, DPI))
    return path


def _tonemap(x, exposure=1.0):
    x = x * exposure
    return 1.0 - np.exp(-np.clip(x, 0, 20))


def _fit(im, out_w_mm, out_h_mm):
    tw = int(round(out_w_mm / 25.4 * DPI))
    th = int(round(out_h_mm / 25.4 * DPI))
    sc = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, int(round(im.width * sc))), max(th, int(round(im.height * sc)))),
                   Image.LANCZOS)
    left = (im.width - tw) // 2
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def _srgb_to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _lin_to_srgb(a):
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)
