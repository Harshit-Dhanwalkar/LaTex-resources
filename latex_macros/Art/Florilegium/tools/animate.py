#!/usr/bin/env python3
"""Animate the growth of one garden: build animation.tex with LuaLaTeX (one page per
frame, split over parallel jobs), rasterize the pages, and write a GIF and, if ffmpeg is
installed, an MP4. The last frame is held for a few seconds before the GIF loops.

    python3 tools/animate.py --seed 7 [--explain] [--fps 20] [--seconds 13] [--jobs 8]
                             [--width 1080] [--gif-width 640] [--hold 3] [--run tools/in-docker]

Writes build/grow-7.gif and build/grow-7.mp4 (build/grow-7-explain.* with --explain);
--out sets the path without the extension.
"""
import argparse
import glob
import os
import shlex
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build(job, a, frames, run, explain, width, framedir):
    """lualatex for frames a..b of `frames`, then one PNG per page, named by frame."""
    first, last = job
    name = f"build/anim-{a.seed}{'-explain' if explain else ''}-{first:04d}"
    defs = (rf"\def\florilegiumseed{{{a.seed}}}\def\animframes{{{frames}}}"
            rf"\def\animfrom{{{first}}}\def\animto{{{last}}}"
            + (r"\def\animexplain{explain}" if explain else ""))
    cmd = shlex.split(run) + ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
                              f"-jobname={name}", defs + r"\input{animation.tex}"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-3000:])
        raise SystemExit(f"frames {first}-{last}: lualatex failed")
    prefix = os.path.join(framedir, f"p{first:04d}")
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
                    f"{name}.pdf", prefix], cwd=ROOT, check=True)
    pages = sorted(glob.glob(prefix + "-*.png"))
    if len(pages) != last - first + 1:
        raise SystemExit(f"frames {first}-{last}: expected {last - first + 1} pages, got {len(pages)}")
    for k, p in enumerate(pages):
        os.replace(p, os.path.join(framedir, f"{first + k:04d}.png"))
    os.remove(os.path.join(ROOT, f"{name}.pdf"))
    return last - first + 1

def gif_pillow(framedir, n, out, fps, hold, width):
    # fallback without ffmpeg: one palette from the last (fullest) frame for every frame
    ims = [Image.open(os.path.join(framedir, f"{k:04d}.png")).convert("RGB") for k in range(1, n + 1)]
    h = round(ims[0].height * width / ims[0].width)
    ims = [im.resize((width, h), Image.LANCZOS) for im in ims]
    pal = ims[-1].quantize(colors=128, dither=Image.Dither.NONE)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
    durs = [round(1000 / fps)] * (n - 1) + [round(1000 / fps + hold * 1000)]
    q[0].save(out, save_all=True, append_images=q[1:], duration=durs, loop=0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--explain", action="store_true", help="mark the free disc each branch grows to")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--seconds", type=float, default=13, help="length of the growth, before the hold")
    ap.add_argument("--hold", type=float, default=3, help="seconds on the finished garden")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 2))
    ap.add_argument("--width", type=int, default=1080, help="frame width in pixels (MP4)")
    ap.add_argument("--gif-width", type=int, default=640)
    ap.add_argument("--run", default="", help="command prefix for lualatex, e.g. tools/in-docker")
    ap.add_argument("--out", help="output path without extension (default build/grow-SEED[-explain])")
    a = ap.parse_args()

    out = a.out or os.path.join("build", f"grow-{a.seed}{'-explain' if a.explain else ''}")
    out = os.path.join(ROOT, out)
    framedir = out + "-frames"
    shutil.rmtree(framedir, ignore_errors=True)
    os.makedirs(framedir)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)

    frames = max(2, round(a.fps * a.seconds))
    per = -(-frames // a.jobs)
    jobs = [(f, min(frames, f + per - 1)) for f in range(1, frames + 1, per)]
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        done = sum(ex.map(lambda j: build(j, a, frames, a.run, a.explain, a.width, framedir), jobs))
    print(f"rendered {done} frames of seed {a.seed} into {os.path.relpath(framedir, ROOT)}")

    pattern = os.path.join(framedir, "%04d.png")
    hold = f"tpad=stop_mode=clone:stop_duration={a.hold}"
    if shutil.which("ffmpeg"):
        ff = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i", pattern]
        subprocess.run(ff + ["-vf", f"{hold},scale={a.gif_width}:-1:flags=lanczos,split[a][b];"
                             "[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
                             "-loop", "0", out + ".gif"], check=True)
        subprocess.run(ff + ["-vf", f"{hold},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
                             "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-movflags", "+faststart",
                             out + ".mp4"], check=True)
        print(f"wrote {os.path.relpath(out, ROOT)}.gif and .mp4")
    else:
        gif_pillow(framedir, frames, out + ".gif", a.fps, a.hold, a.gif_width)
        print(f"wrote {os.path.relpath(out, ROOT)}.gif (no ffmpeg, so no MP4)")

if __name__ == "__main__":
    main()
