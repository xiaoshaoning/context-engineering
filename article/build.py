"""Download the slides, trace them to SVG/PDF, and write build/build.md for pandoc.

Usage: python build.py [--force]   (--force re-traces slides that are already done)
"""
import os, re, subprocess, sys, urllib.request
import numpy as np
import vtracer
from PIL import Image

BUILD = "build"          # intermediates: downloaded slides, traced PDFs, previews
BASE = "https://www.dbreunig.com/img/agnt_con"

# A traced slide replaces the JPEG only if it still looks like the original after
# rendering (mean pixel error <= 6/255) and stays a sane size. Photographs and
# gradient-heavy charts fail this and stay raster; 3 of 39 slides do.
FAITHFUL_ERROR, FAITHFUL_KB = 6.0, 1200.0


def is_faithful(mean_pixel_error, kb):
    return mean_pixel_error <= FAITHFUL_ERROR and kb <= FAITHFUL_KB


def mean_pixel_error(left, right):
    a = np.asarray(Image.open(left).convert("RGB"), dtype=np.float32)
    b = np.asarray(Image.open(right).convert("RGB"), dtype=np.float32)
    return float(np.abs(a - b).mean())


def fetch(name):
    """Download one slide JPEG if it is not already on disk."""
    path = f"{BUILD}/img/{name}.jpeg"
    if not os.path.exists(path):
        urllib.request.urlretrieve(f"{BASE}/{name}.jpeg", path)
    return path


def trace(name):
    """Vectorize one slide; return (mean pixel error vs the JPEG, SVG size in KB)."""
    src = fetch(name)
    svg = f"svg/{name}.svg"
    vtracer.convert_image_to_svg_py(src, svg, colormode="color", hierarchical="stacked",
                                    mode="spline", filter_speckle=8,
                                    color_precision=8, layer_difference=8)
    preview = f"{BUILD}/out/{name}.png"
    subprocess.run(["rsvg-convert", "-w", "1920", "-h", "1080", "-o", preview, svg], check=True)
    return mean_pixel_error(src, preview), os.path.getsize(svg) / 1024


def write_figure(name, svg, error, kb):
    """Keep the slide as a vector PDF, or fall back to a downscaled raster. -> include path"""
    pdf, jpg = f"{BUILD}/figs/{name}.pdf", f"{BUILD}/figs/{name}.jpg"
    if is_faithful(error, kb):
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        stale = jpg
    else:
        Image.open(f"{BUILD}/img/{name}.jpeg").resize(
            (1600, 900), Image.LANCZOS).save(jpg, quality=88)
        stale = pdf
    if os.path.exists(stale):        # a retrace may flip the decision
        os.remove(stale)
    return pdf if os.path.exists(pdf) else jpg


def figure_path(name):
    pdf = f"{BUILD}/figs/{name}.pdf"
    return pdf if os.path.exists(pdf) else f"{BUILD}/figs/{name}.jpg"


def main(force):
    for sub in ("figs", "out", "img"):
        os.makedirs(f"{BUILD}/{sub}", exist_ok=True)

    names = sorted({re.search(r"(AGNT_Con\.\d+)", url).group(1)
                    for url in open("urls.txt", encoding="utf-8")})
    md = open("post.md", encoding="utf-8").read()
    traced = 0
    for name in names:
        if force or not os.path.exists(figure_path(name)):
            svg = f"svg/{name}.svg"
            error, kb = trace(name)
            target = write_figure(name, svg, error, kb)
            traced += 1
            print(f"{name}: error={error:.2f}/255 size={kb:.0f}KB "
                  f"-> {'svg' if target.endswith('.pdf') else 'raster'}")
        else:
            target = figure_path(name)
        md = md.replace(f"{BASE}/{name}.jpeg", target)

    md = md.split("<style>")[0].rstrip() + (
        "\n\n-----\n\n*Originally published at "
        "<https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html> "
        "on 24 October 2026. Slides by Drew Breunig (Cmpnd); text reproduced here for "
        "reading offline. Slide images were vectorized from the original JPEGs.*\n")
    open(f"{BUILD}/build.md", "w", encoding="utf-8").write(md)

    vector = sum(1 for name in names if figure_path(name).endswith(".pdf"))
    print(f"traced this run: {traced} | vector: {vector}/{len(names)}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
