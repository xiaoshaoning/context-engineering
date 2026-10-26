"""Vectorize slide images -> SVG -> PDF, fall back to raster for photo-heavy slides."""
import os, re, subprocess, sys
import numpy as np
import vtracer
from PIL import Image

os.makedirs("figs", exist_ok=True)
os.makedirs("out", exist_ok=True)

def trace(name):
    src = f"img/{name}.jpeg"
    svg = f"svg/{name}.svg"
    vtracer.convert_image_to_svg_py(src, svg, colormode="color", hierarchical="stacked",
                                    mode="spline", filter_speckle=8,
                                    color_precision=8, layer_difference=8)
    png = f"out/{name}.png"
    subprocess.run(["rsvg-convert", "-w", "1920", "-h", "1080", "-o", png, svg], check=True)
    a = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32)
    b = np.asarray(Image.open(src).convert("RGB"), dtype=np.float32)
    diff = float(np.abs(a - b).mean())
    kb = os.path.getsize(svg) / 1024
    return svg, diff, kb

names = sorted({re.search(r"(AGNT_Con\.\d+)", u).group(1) for u in open("urls.txt")})

md = open("post.md", encoding="utf-8").read()
stats = []
for name in names:
    svg, diff, kb = trace(name)
    ok = diff <= 6.0 and kb <= 1200
    if ok:  # keep real vector
        pdf = f"figs/{name}.pdf"
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o", pdf, svg], check=True)
        target = pdf
    else:   # photo: keep raster, downscaled for PDF size
        jpg = f"figs/{name}.jpg"
        im = Image.open(f"img/{name}.jpeg")
        im.resize((1600, 900), Image.LANCZOS).save(jpg, quality=88)
        target = jpg
    stats.append((name, round(diff, 2), round(kb), "svg" if ok else "raster"))
    md = md.replace(f"https://www.dbreunig.com/img/agnt_con/{name}.jpeg", target)

md = md.split("<style>")[0].rstrip() + (
    "\n\n-----\n\n*Originally published at "
    "<https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html> "
    "on 24 October 2026. Slides by Drew Breunig (Cmpnd); text reproduced here for "
    "reading offline. Slide images were vectorized from the original JPEGs.*\n")
open("build.md", "w", encoding="utf-8").write(md)
for s in stats:
    print(*s)
print("vectorized:", sum(1 for s in stats if s[3] == "svg"), "/", len(stats))
