"""Render one scientific example; opt into the gallery or full PDF checks."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "simple": ("simple_plot.py", "simple-plot"),
    "calibration": ("scientific_plots.py", "calibration"),
    "spectrum": ("scientific_plots.py", "spectrum"),
    "heatmap": ("scientific_plots.py", "heatmap"),
    "distribution": ("scientific_plots.py", "distribution"),
    "data": ("data_plot.py", "data-plot"),
    "optical": ("optical_schematic.py", "optical-schematic"),
    "network": ("network.py", "network"),
    "comparison": ("style_comparison.py", "style-comparison"),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory, relative to your current directory.")
    parser.add_argument("--example", choices=[*EXAMPLES, "all"], default="simple", help="Default: one lightweight data plot. Use all to render the gallery.")
    parser.add_argument("--check", action="store_true", help="Also run PDF text/collision checks and render a preview for each selected example.")
    parser.add_argument("--portable", action="store_true", help="Use Matplotlib's bundled DejaVu Sans/Serif for this demo.")
    parser.add_argument("--body-font", help="Default: Arial, or DejaVu Sans with --portable.")
    parser.add_argument("--math-font", help="Default: Times New Roman, or DejaVu Serif with --portable.")
    parser.add_argument("--font-dir", type=Path, help="Register your own TTF/OTF files.")
    args = parser.parse_args(argv)
    if args.portable and (args.body_font or args.math_font):
        parser.error("Choose --portable or explicit --body-font/--math-font values.")

    required = ["matplotlib", "numpy"] + (["pymupdf"] if args.check else [])
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        parser.exit(1, "Missing Python dependencies: " + ", ".join(missing) + "\n"
                    + f'Install them with this interpreter:\n  "{sys.executable}" -m pip install -r "{ROOT / "requirements.txt"}"\n')

    body_font = "DejaVu Sans" if args.portable else args.body_font or "Arial"
    math_font = "DejaVu Serif" if args.portable else args.math_font or "Times New Roman"
    from ohmyplt import configure
    try:
        configure(body_font, math_font, args.font_dir)
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\nTo try the examples with bundled fonts, add --portable.\n")

    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    font_args = ["--body-font", body_font, "--math-font", math_font]
    if args.font_dir:
        font_args += ["--font-dir", str(args.font_dir.expanduser().resolve())]
    print(f"Fonts: {body_font} / {math_font}", flush=True)
    print(f"Output: {out}", flush=True)
    commands = []
    selected = list(EXAMPLES) if args.example == "all" else [args.example]
    for name in selected:
        filename, stem = EXAMPLES[name]
        kind_args = ["--kind", name] if filename == "scientific_plots.py" else []
        commands.append(([f"examples/{filename}", "--out", str(out), *font_args, *kind_args], f"render {stem}"))
        if args.check:
            families = [body_font, math_font] + (["DejaVu Sans"] if name == "comparison" else [])
            allowed_fonts = [argument for family in families for argument in ("--allow-font", family)]
            commands.extend([
                (["scripts/preflight.py", str(out / f"{stem}.pdf"), "--out", str(out / "qa" / stem), *allowed_fonts], f"inspect {stem}"),
                (["scripts/preview.py", str(out / f"{stem}.pdf"), "--out", str(out / f"{stem}.preview.png"), "--dpi", "108"], f"preview {stem}"),
            ])
    for command, label in commands:
        print(f"\n[{label}]", flush=True)
        result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / command[0]), *command[1:]])
        if result.returncode:
            print(f"Stopped at {label}. See the command output and {out / 'qa'}.", file=sys.stderr)
            return result.returncode

    summary = {"body_font": body_font, "math_font": math_font, "portable": args.portable,
               "examples": [EXAMPLES[name][1] for name in selected],
               "preflight": "passed" if args.check else "not requested"}
    (out / "quickstart.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("\nDone: figures, example data and manifests are in the output directory."
          + (" PDF reports and previews are included." if args.check else " Add --check for PDF reports and previews."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
