#!/usr/bin/env python3
"""Render a gallery sheet: build gallery.tex once per variant with LuaLaTeX, rasterize
each page and write a contact sheet (and, for seeds, a GIF with one frame per seed).

    python3 tools/gallery.py --seeds 1 2 3 4 5 6     -> gallery/seeds.png + seeds.gif
    python3 tools/gallery.py --seed 6 --inks 2456C4 5B2A1F   -> gallery/inks.png
    python3 tools/gallery.py --seed 6 --ages 0 0.5 1         -> gallery/seasons.png
Options: [--dpi 50] [--jobs 4] [--run tools/in-docker]
"""
import argparse
import os
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = (36, 86, 196)

def build(v, dpi, run):
    """v = (name, label, seed, ink, age): one page -> build/<name>.png"""
    name, _, seed, ink, age = v
    job = f"build/{name}"
    defs = rf"\def\florilegiumseed{{{seed}}}"
    if ink: defs += rf"\def\galleryink{{{ink}}}"
    if age is not None: defs += rf"\def\galleryage{{{age}}}"
    cmd = shlex.split(run) + ["lualatex", "-interaction=nonstopmode", "-halt-on-error", f"-jobname={job}",
                              defs + r"\input{gallery.tex}"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-3000:])
        raise SystemExit(f"{name}: lualatex failed")
    png = os.path.join(ROOT, "build", name)
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", f"{job}.pdf", png], cwd=ROOT, check=True)
    return png + ".png"

def season(a):
    a = float(a)
    return "spring" if a < 0.17 else "early summer" if a < 0.5 else "late summer" if a < 0.83 else "autumn"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--seed", type=int, default=6, help="the seed of the ink and season sheets")
    ap.add_argument("--inks", nargs="+", help="HTML colors: one page per ink -> gallery/inks.png")
    ap.add_argument("--ages", nargs="+", help="ages 0..1: one page per age -> gallery/seasons.png")
    ap.add_argument("--dpi", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--run", default="", help="command prefix for lualatex, e.g. tools/in-docker")
    a = ap.parse_args()
    if a.inks:
        kind, cols = "inks", 3
        variants = [(f"ink-{c}", "#" + c.upper(), a.seed, c, None) for c in a.inks]
    elif a.ages:
        kind, cols = "seasons", len(a.ages)
        variants = [(f"age-{x}", season(x), a.seed, None, x) for x in a.ages]
    else:
        kind, cols = "seeds", 3
        variants = [(f"seed-{s}", f"seed {s}", s, None, None) for s in a.seeds]
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "gallery"), exist_ok=True)
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        paths = list(ex.map(lambda v: build(v, a.dpi, a.run), variants))
    frames = []
    for v, path in zip(variants, paths):
        im = Image.open(path).convert("RGB")
        d = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", max(12, im.width // 30))
        except OSError:
            font = ImageFont.load_default()
        color = tuple(int(v[3][i:i + 2], 16) for i in (0, 2, 4)) if v[3] else BLUE
        d.text((im.width - 10, im.height - 10), v[1], fill=color, font=font, anchor="rd")
        frames.append(im)
    cols = min(cols, len(frames)); rows = (len(frames) + cols - 1) // cols
    w, h = frames[0].size
    sheet = Image.new("RGB", (cols * w + (cols + 1) * 8, rows * h + (rows + 1) * 8), (235, 235, 240))
    for i, im in enumerate(frames):
        sheet.paste(im, (8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 8)))
    sheet.save(os.path.join(ROOT, "gallery", f"{kind}.png"))
    if kind == "seeds":
        frames[0].save(os.path.join(ROOT, "gallery", "seeds.gif"), save_all=True, append_images=frames[1:],
                       duration=900, loop=0, optimize=False)
    print(f"wrote gallery/{kind}.png:", ", ".join(v[1] for v in variants))

if __name__ == "__main__":
    main()
