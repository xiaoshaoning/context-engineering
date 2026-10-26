"""Download the slides, trace them to SVG/PDF, and write build/build.md for pandoc.

Usage: python build.py [--force]   (--force re-traces slides that are already done)
"""
import os, re, subprocess, sys, urllib.request
import numpy as np
import vtracer
from PIL import Image

BUILD = "build"          # intermediates: downloaded slides, traced PDFs, previews
os.makedirs(f"{BUILD}/figs", exist_ok=True)
os.makedirs(f"{BUILD}/out", exist_ok=True)
os.makedirs(f"{BUILD}/img", exist_ok=True)

BASE = "https://www.dbreunig.com/img/agnt_con"

def fetch(name):
    """Download one slide JPEG if it is not already on disk."""
    path = f"{BUILD}/img/{name}.jpeg"
    if not os.path.exists(path):
        urllib.request.urlretrieve(f"{BASE}/{name}.jpeg", path)
    return path

def trace(name):
    src = fetch(name)
    svg = f"svg/{name}.svg"
    vtracer.convert_image_to_svg_py(src, svg, colormode="color", hierarchical="stacked",
                                    mode="spline", filter_speckle=8,
                                    color_precision=8, layer_difference=8)
    png = f"{BUILD}/out/{name}.png"
    subprocess.run(["rsvg-convert", "-w", "1920", "-h", "1080", "-o", png, svg], check=True)
    a = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32)
    b = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32)
    diff = float(np.abs(a - b).mean())
    kb = os.path.getsize(svg) / 1024
    return svg, diff, kb

FORCE = "--force" in sys.argv
names = sorted({re.search(r"(AGNT_Con\.\d+)", u).group(1) for u in open("urls.txt")})

md = open("post.md", encoding="utf-8").read()
stats = []
for name in names:
    pdf, jpg = f"{BUILD}/figs/{name}.pdf", f"{BUILD}/figs/{name}.jpg"
    if FORCE or not (os.path.exists(pdf) or os.path.exists(jpg)):
        svg, diff, kb = trace(name)
        if diff <= 6.0 and kb <= 1200:          # real vector keeps the slide
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        else:                                   # photo: raster, downscaled
            Image.open(f"{BUILD}/img/{name}.jpeg").resize(
                (1600, 900), Image.LANCZOS).save(jpg, quality=88)
        stats.append((name, round(diff, 2), round(kb)))
    target = pdf if os.path.exists(pdf) else jpg
    md = md.replace(f"https://www.dbreunig.com/img/agnt_con/{name}.jpeg", target)

md = md.split("<style>")[0].rstrip() + (
    "\n\n-----\n\n*Originally published at "
    "<https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html> "
    "on 24 October 2026. Slides by Drew Breunig (Cmpnd); text reproduced here for "
    "reading offline. Slide images were vectorized from the original JPEGs.*\n")
open(f"{BUILD}/build.md", "w", encoding="utf-8").write(md)
print("traced:", len(stats), "| vector:", sum(1 for n in names
                                           if os.path.exists(f"{BUILD}/figs/{n}.pdf")),
      "/", len(names))
