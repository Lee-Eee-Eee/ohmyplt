"""Build the 18-second README walkthrough from checked repository artifacts.

Requires the Python requirements and ffmpeg on PATH. Temporary frames and PDF
inspection reports go to --work; only GIF, MP4 and a source manifest go to --out.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pymupdf
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
SIZE = (1120, 700)
FPS = 6
COUNTS = (24, 27, 30, 27)
INK, MUTED, TEAL = "#183449", "#536975", "#16766b"
PAPER, LINE = "#f4f7f8", "#dbe5e9"


def font(size, *, mono=False, bold=False):
    families = ["Consolas", "DejaVu Sans Mono"] if mono else ["Arial", "DejaVu Sans"]
    for family in families:
        try:
            path = font_manager.findfont(
                font_manager.FontProperties(family=family, weight="bold" if bold else "normal"),
                fallback_to_default=False,
            )
            return ImageFont.truetype(path, size)
        except ValueError:
            continue
    raise RuntimeError("No walkthrough UI font found.")


def label(draw, xy, text, size=20, color=INK, **kwargs):
    draw.text(xy, text, fill=color, font=font(size, **kwargs))


def base(stage, title, subtitle):
    image = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(image)
    label(draw, (40, 23), "ohmyplt", 37, bold=True)
    label(draw, (751, 39), "SEEDED EXAMPLE / 18-SECOND TOUR", 16, TEAL, bold=True)
    draw.line((40, 86, 1080, 86), fill=LINE, width=2)
    label(draw, (40, 103), title, 29, bold=True)
    label(draw, (40, 143), subtitle, 18, MUTED)
    steps = ["1  Model source", "2  Architecture", "3  Operations", "4  Vector exports"]
    for index, text in enumerate(steps):
        x = 40 + index * 265
        active = index == stage
        draw.rounded_rectangle((x, 648, x + 245, 684), radius=9,
                               fill=TEAL if active else "#e5ecef")
        label(draw, (x + 13, 656), text, 17, "white" if active else MUTED, bold=active)
    return image


def card(image, box):
    ImageDraw.Draw(image).rounded_rectangle(box, radius=13, fill="white", outline=LINE, width=2)


def fit(image, picture, box):
    picture = picture.convert("RGB")
    picture.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    image.paste(picture, (box[0] + (box[2] - box[0] - picture.width) // 2,
                          box[1] + (box[3] - box[1] - picture.height) // 2))


def render(page, clip=None, scale=3):
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip, alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def crop_mm(page, x, y, width, height):
    # Figure coordinates start at the lower left; PDF clips start at the top left.
    unit = 72 / 25.4
    return render(page, pymupdf.Rect(x * unit, page.rect.height - (y + height) * unit,
                                    (x + width) * unit, page.rect.height - y * unit), scale=5)


def load_model():
    spec = importlib.util.spec_from_file_location("walkthrough_model", ROOT / "examples/residual_model.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with np.load(ROOT / "assets/gallery/network-demo.npz", allow_pickle=False) as archive:
        fixed, correction, prediction = module.predict(archive["features"], archive)
    np.testing.assert_allclose(prediction, fixed + correction)
    return prediction


def scenes(report, prediction):
    with pymupdf.open(ROOT / "assets/gallery/network.pdf") as document:
        page = document[0]
        overview = render(page)
        dense = crop_mm(page, 61, 24, 27, 30)
        merge = crop_mm(page, 142, 29, 34, 49)

    first = base(0, "Start with the operations", "A runnable NumPy example: GRU + dense layers + a fixed affine branch.")
    card(first, (40, 186, 770, 583))
    draw = ImageDraw.Draw(first)
    label(draw, (62, 202), "examples/residual_model.py", 18, TEAL, mono=True)
    source = (ROOT / "examples/residual_model.py").read_text(encoding="utf8").splitlines()
    # Display exact source lines, including the gap between the two excerpts.
    start = next(i for i, line in enumerate(source) if "reset = _sigmoid" in line)
    affine = next(i for i, line in enumerate(source) if 'correction = parameters["W2"]' in line)
    snippet = [*source[start:start + 4], "", *source[affine:affine + 3]]
    for index, line in enumerate(snippet):
        label(draw, (62, 245 + index * 35), line.strip(), 17, mono=True)
    for y, value, name in [(195, "9 x 27", "history features"), (327, "32", "GRU hidden units"), (459, "8", "output channels")]:
        card(first, (793, y, 1080, y + 118))
        label(draw, (817, y + 14), value, 38, TEAL, bold=True)
        label(draw, (817, y + 73), name, 19, MUTED)
    label(draw, (40, 606), "Seeded signals and initialized weights / forward inference", 18, MUTED)

    second = base(1, "Read the full architecture", "The checked gallery figure, rendered directly from its PDF.")
    card(second, (40, 184, 1080, 594))
    fit(second, overview, (53, 195, 1067, 583))
    label(ImageDraw.Draw(second), (40, 610), "History -> GRU -> Dense -> GELU -> Linear -> residual sum", 18, MUTED)

    third = base(2, "Zoom into the actual drawing", "Weight matrices, biases and explicit ports stay visible in the exported figure.")
    card(third, (40, 185, 545, 594))
    card(third, (566, 185, 1080, 594))
    draw = ImageDraw.Draw(third)
    label(draw, (63, 201), "Weights + bias", 21, TEAL, bold=True)
    label(draw, (590, 201), "Residual merge", 21, TEAL, bold=True)
    fit(third, dense, (74, 243, 510, 575))
    fit(third, merge, (593, 243, 1054, 575))
    label(draw, (40, 610), "PDF crops / the same figure and demonstration arrays", 18, MUTED)

    fourth = base(3, "Keep the figure editable", "Exported files, Python source and inspection results travel together.")
    card(fourth, (40, 185, 623, 594))
    card(fourth, (645, 185, 1080, 594))
    draw = ImageDraw.Draw(fourth)
    label(draw, (65, 207), "assets/gallery/", 21, TEAL, mono=True, bold=True)
    for index, (name, purpose) in enumerate([
        ("network.svg", "editable text"), ("network.pdf", "embedded fonts"),
        ("network.png", "quick preview"), ("network-demo.npz", "example arrays"),
    ]):
        y = 258 + index * 54
        label(draw, (66, y), name, 22, mono=True)
        label(draw, (388, y + 3), purpose, 17, MUTED)
    label(draw, (65, 501), "examples/network.py", 21, mono=True)
    label(draw, (65, 537), "examples/residual_model.py", 21, mono=True)
    label(draw, (670, 207), "PDF preflight", 24, bold=True)
    for index, key in enumerate(("text", "collision", "fonts")):
        status = "PASS" if report["checks"][key] == 0 else "FAIL"
        label(draw, (673, 260 + index * 47), status, 22, TEAL, bold=True)
        label(draw, (759, 263 + index * 47), {"text": "glyph size", "collision": "layout collisions", "fonts": "Arial / Times"}[key], 20)
    label(draw, (670, 426), "Example inference", 20, bold=True)
    label(draw, (670, 464), "y[0] = " + f"{prediction[0]:.3f}", 23, TEAL, mono=True)
    label(draw, (670, 505), "8 finite output values", 18, MUTED)
    label(draw, (40, 610), "Run: python scripts/quickstart.py --portable --out output", 18, MUTED, mono=True)
    return [first, second, third, fourth]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "assets/demo")
    parser.add_argument("--work", type=Path, default=ROOT / "output/demo")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("Install ffmpeg and place it on PATH to rebuild the walkthrough.")
    out, work = args.out.resolve(), args.work.resolve()
    out.mkdir(parents=True, exist_ok=True)
    frames = work / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/preflight.py"),
                    str(ROOT / "assets/gallery/network.pdf"), "--out", str(work / "qa"),
                    "--allow-font", "Arial", "--allow-font", "TimesNewRoman"], check=True)
    report = json.loads((work / "qa/report.json").read_text(encoding="utf8"))
    pictures = scenes(report, load_model())
    offset = 0
    for stage, (picture, count) in enumerate(zip(pictures, COUNTS)):
        picture.save(work / f"scene-{stage + 1}.png")
        for index in range(count):
            frame = picture
            if stage and index < 3:
                frame = Image.blend(pictures[stage - 1], picture, (index + 1) / 3)
            frame.save(frames / f"frame-{offset:03}.png")
            offset += 1
    common = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(FPS),
              "-i", str(frames / "frame-%03d.png"), "-frames:v", str(offset)]
    subprocess.run([*common, "-filter_complex",
                    "split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=none",
                    "-loop", "0", str(out / "walkthrough.gif")], check=True)
    subprocess.run([*common, "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(out / "walkthrough.mp4")], check=True)
    paths = ["examples/residual_model.py", "examples/network.py", "assets/gallery/network.pdf",
             "assets/gallery/network-demo.npz", "scripts/build_demo.py"]
    manifest = {"kind": "rendered walkthrough of the seeded repository example", "duration_seconds": offset / FPS,
                "fps": FPS, "size": list(SIZE), "frames": offset, "pdf_inspection": report,
                "sources_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    print(f"Created {out / 'walkthrough.gif'} and {out / 'walkthrough.mp4'}")


if __name__ == "__main__":
    main()
