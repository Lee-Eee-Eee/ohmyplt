"""Render and inspect the bundled examples with one explicit font choice."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory, relative to your current directory.")
    parser.add_argument("--portable", action="store_true", help="Use Matplotlib's bundled DejaVu Sans/Serif for this demo.")
    parser.add_argument("--body-font", help="Default: Arial, or DejaVu Sans with --portable.")
    parser.add_argument("--math-font", help="Default: Times New Roman, or DejaVu Serif with --portable.")
    parser.add_argument("--font-dir", type=Path, help="Register your own TTF/OTF files.")
    args = parser.parse_args(argv)
    if args.portable and (args.body_font or args.math_font):
        parser.error("Choose --portable or explicit --body-font/--math-font values.")

    missing = [name for name in ("matplotlib", "numpy", "pymupdf") if importlib.util.find_spec(name) is None]
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
    commands = [(["scripts/doctor.py", *font_args], "font check")]
    examples = [("network.py", "network"), ("data_plot.py", "data-plot"), ("style_comparison.py", "style-comparison")]
    for filename, stem in examples:
        commands.extend([
            ([f"examples/{filename}", "--out", str(out), *font_args], f"render {stem}"),
            (["scripts/preflight.py", str(out / f"{stem}.pdf"), "--out", str(out / "qa" / stem)], f"inspect {stem}"),
            (["scripts/preview.py", str(out / f"{stem}.pdf"), "--out", str(out / f"{stem}.preview.png"), "--dpi", "108"], f"preview {stem}"),
        ])
    for command, label in commands:
        print(f"\n[{label}]", flush=True)
        result = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / command[0]), *command[1:]])
        if result.returncode:
            print(f"Stopped at {label}. See the command output and {out / 'qa'}.", file=sys.stderr)
            return result.returncode

    summary = {"body_font": body_font, "math_font": math_font, "portable": args.portable,
               "examples": [stem for _, stem in examples], "preflight": "passed"}
    (out / "quickstart.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("\nDone: PNG, SVG, PDF, sample data, manifests and inspection reports are in the output directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
