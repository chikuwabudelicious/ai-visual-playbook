# -*- coding: utf-8 -*-
"""Turn a generated 3:1 panorama (image-prompt-recipes, style S6/S7) into a slide-bottom band.

    python make_band.py panorama_town.png -o bands/watercolor_town.webp

Keeps the bottom strip (height = width/12, where the scenery sits), resizes to 2400x200,
makes the flat background colour transparent and fades the top edge so the band blends into any slide.
"""
import argparse
from PIL import Image, ImageChops, ImageFilter


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"), ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--tol", type=int, default=18, help="how close to the background colour counts as background")
    a = ap.parse_args()
    im = Image.open(a.src).convert("RGB")
    w, h = im.size
    bg = im.getpixel((w // 2, 2))                       # the empty flat area at the top
    strip = im.crop((0, h - w // 12, w, h)).resize((2400, 200), Image.LANCZOS)
    # alpha 1: pixels near the background colour become transparent (soft edge)
    diff = ImageChops.difference(strip, Image.new("RGB", strip.size, bg)).convert("L")
    alpha = diff.point(lambda v: 0 if v < a.tol else min(255, (v - a.tol) * 8)).filter(ImageFilter.GaussianBlur(1.2))
    # alpha 2: fade the top 35% so no hard cut line shows
    fade = Image.linear_gradient("L").resize((2400, 200))           # 0 at top -> 255 at bottom
    fade = fade.point(lambda v: min(255, int(v / 0.35)))
    out = strip.convert("RGBA")
    out.putalpha(ImageChops.multiply(alpha, fade))
    out.save(a.out, "WEBP", quality=90, method=6)
    print("OK", a.out)


if __name__ == "__main__":
    main()
