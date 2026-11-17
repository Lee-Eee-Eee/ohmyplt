"""Audit PDF text, layout, fonts and optional all-vector delivery."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import pymupdf


def inspect_resources(document):
    """Inspect displayed images and embedded font programs in the actual PDF."""
    images = []
    font_records = {}
    for page_number, page in enumerate(document, 1):
        for image in page.get_image_info():
            images.append({"page": page_number, "bbox": list(image["bbox"]),
                           "width": image["width"], "height": image["height"]})
        for xref, extension, font_type, name, *_ in page.get_fonts(full=True):
            font_records[xref] = {"name": name, "type": font_type,
                                  "extension": extension,
                                  "embedded": bool(document.extract_font(xref)[3])}
    return images, list(font_records.values())


def normalized_font(name):
    return "".join(character for character in name.lower() if character.isalnum())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-pt", type=float, default=5)
    parser.add_argument("--allow-font", action="append", default=[])
    parser.add_argument("--vector-only", action="store_true",
                        help="Fail if the PDF displays any raster images.")
    parser.add_argument("--require-embedded-fonts", action="store_true",
                        help="Fail if any referenced PDF font lacks an embedded font program.")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    base = Path(__file__).resolve().parents[1] / "vendor/nature_figure"
    checks = {}
    audits = [
        ("text", "audit_pdf_text.py", [str(args.pdf), "--min-pt", str(args.min_pt), "--json"]),
        ("collision", "audit_figure_collisions.py",
         [str(args.pdf), "--json-out", str(args.out / "collisions.json")]),
    ]
    for name, script, audit_args in audits:
        result = subprocess.run([sys.executable, "-X", "utf8", str(base / script), *audit_args],
                                capture_output=True, text=True, encoding="utf8")
        (args.out / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf8")
        checks[name] = result.returncode

    with pymupdf.open(args.pdf) as document:
        fonts = sorted({span["font"] for page in document
                        for block in page.get_text("dict")["blocks"] if "lines" in block
                        for line in block["lines"] for span in line["spans"]})
        images, font_records = inspect_resources(document)
        pages_mm = [[page.rect.width * 25.4 / 72, page.rect.height * 25.4 / 72]
                    for page in document]

    unexpected = [font for font in fonts if args.allow_font and not any(
        normalized_font(allowed) in normalized_font(font) for allowed in args.allow_font)]
    unembedded = [font["name"] for font in font_records if not font["embedded"]]
    checks["fonts"] = int(bool(unexpected))
    checks["raster_images"] = int(args.vector_only and bool(images))
    checks["font_embedding"] = int(args.require_embedded_fonts and bool(unembedded))
    report = {"checks": checks, "fonts": fonts, "unexpected_fonts": unexpected,
              "raster_images": images, "font_resources": font_records,
              "unembedded_fonts": unembedded, "pages_mm": pages_mm}
    (args.out / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if all(code == 0 for code in checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
