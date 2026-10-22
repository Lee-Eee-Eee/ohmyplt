"""Compose the README overview from the exported scientific example PNGs."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gallery", type=Path, default=ROOT / "assets/gallery")
    args = parser.parse_args()
    path = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    title_font = ImageFont.truetype(path, 24)
    image = Image.new("RGB", (1440, 1010), "#f4f7f8")
    draw = ImageDraw.Draw(image)
    panels = [
        ("simple-plot", "Single-column data plot", (20, 20, 473, 485)),
        ("calibration", "Fit + residual", (493, 20, 946, 485)),
        ("spectrum", "Count spectrum", (966, 20, 1420, 485)),
        ("heatmap", "Spatial fields + signed error", (20, 505, 946, 990)),
        ("distribution", "Independent cases", (966, 505, 1420, 990)),
    ]
    for stem, title, box in panels:
        draw.rounded_rectangle(box, radius=14, fill="white", outline="#dbe5e9", width=2)
        draw.text((box[0] + 20, box[1] + 17), title, font=title_font, fill="#183449")
        with Image.open(args.gallery / f"{stem}.png") as source:
            picture = source.convert("RGB")
        width, height = box[2] - box[0] - 24, box[3] - box[1] - 76
        picture.thumbnail((width, height), Image.Resampling.LANCZOS)
        image.paste(picture, (box[0] + (box[2] - box[0] - picture.width) // 2,
                             box[1] + 64 + (height - picture.height) // 2))
    image.save(args.gallery / "overview.png", optimize=True)
    print(args.gallery / "overview.png")


if __name__ == "__main__":
    main()
