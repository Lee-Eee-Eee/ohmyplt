"""Compare Matplotlib defaults and ohmyplt on identical seeded time-series data.

Run from the repository root, for example::

    python examples/style_comparison.py --out assets/gallery

The figure, source arrays, caption, manifest, and comparison check all go to
the directory selected with ``--out``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ohmyplt import (  # noqa: E402
    BLUE,
    RUST,
    apply_chart_style,
    check_axes_alignment,
    configure,
    export,
)
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

SEED = 19
XLABEL = r"Time $t$ (s)"
YLABEL = r"Signal $s(t)$ (a.u.)"
CAPTION = "Same seeded data and axis limits in both panels."


def add_curves(ax, time, reference, observation, styled=False):
    """Keep every data and axis choice common to both panels."""
    options = (
        ({"color": BLUE, "lw": 1.0}, {"color": RUST, "lw": 0.8})
        if styled
        else ({}, {})
    )
    ax.plot(time, reference, label="Reference", **options[0])
    ax.plot(time, observation, label="Observation", **options[1])
    ax.set_xscale("linear")
    ax.set_yscale("linear")
    ax.set(
        xlim=(0, 30),
        ylim=(-1.5, 1.9),
        xticks=[0, 10, 20, 30],
        yticks=[-1, 0, 1],
        xlabel=XLABEL,
        ylabel=YLABEL,
    )
    if styled:
        ax.legend(loc="upper right", frameon=False, fontsize=7)
    else:
        ax.legend(loc="upper right")


def verify_comparison(fig, baseline, styled):
    """Fail if a styling edit changes the numerical comparison."""
    for left, right in zip(baseline.lines, styled.lines):
        np.testing.assert_array_equal(left.get_xdata(), right.get_xdata())
        np.testing.assert_array_equal(left.get_ydata(), right.get_ydata())
        assert left.get_label() == right.get_label()
    assert len(baseline.lines) == len(styled.lines) == 2
    for getter in ("get_xlim", "get_ylim", "get_xticks", "get_yticks"):
        np.testing.assert_array_equal(getattr(baseline, getter)(), getattr(styled, getter)())
    for getter in ("get_xscale", "get_yscale", "get_xlabel", "get_ylabel"):
        assert getattr(baseline, getter)() == getattr(styled, getter)()
    alignment = check_axes_alignment(fig, [baseline, styled])
    if not alignment["passed"]:
        raise RuntimeError("The two plotting rectangles must have equal dimensions.")
    return {"identical_data_and_axes": True, "line_count_per_panel": 2, **alignment}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--body-font", default="Arial")
    parser.add_argument("--math-font", default="Times New Roman")
    parser.add_argument("--font-dir")
    args = parser.parse_args()

    rng = np.random.default_rng(SEED)
    time = np.linspace(0, 30, 121)
    reference = np.sin(time / 3) + 0.15 * np.cos(time / 1.5)
    observation = reference + rng.normal(0, 0.11, len(time))
    work = args.out
    work.mkdir(parents=True, exist_ok=True)
    data = work / "style-comparison-data.npz"
    np.savez_compressed(data, time=time, reference=reference, observation=observation)

    # Create the left panel under the actual Matplotlib defaults. Typography,
    # line widths/colors, ticks, spines and the legend are left untouched.
    with mpl.rc_context(rc=mpl.rcParamsDefault):
        fig = plt.figure(figsize=(210 / 25.4, 96 / 25.4))
        baseline = fig.add_axes([0.085, 0.27, 0.375, 0.55])
        add_curves(baseline, time, reference, observation)
        baseline.set_title("Matplotlib defaults", pad=10)
        # Math font selection is normally resolved at render time. Freeze the
        # left labels to its default before configuring the right panel.
        for label in (baseline.xaxis.label, baseline.yaxis.label):
            label.set_math_fontfamily(mpl.rcParamsDefault["mathtext.fontset"])
        baseline_fonts = {
            "body_font": mpl.rcParamsDefault["font.family"],
            "mathtext_fontset": mpl.rcParamsDefault["mathtext.fontset"],
            "font_size_pt": mpl.rcParamsDefault["font.size"],
        }

        configure(args.body_font, args.math_font, args.font_dir)
        styled = fig.add_axes([0.595, 0.27, 0.375, 0.55])
        add_curves(styled, time, reference, observation, styled=True)
        styled.set_title("ohmyplt", fontsize=10, pad=10)
        apply_chart_style(styled)
        fig.text(0.5, 0.055, CAPTION, ha="center", va="center", fontsize=8)

        checks = verify_comparison(fig, baseline, styled)
        (work / "style-comparison.checks.json").write_text(
            json.dumps(checks, indent=2) + "\n", encoding="utf8"
        )
        stem = args.out / "style-comparison"
        manifest = export(fig, stem, dpi=300, source_files=[__file__, data])
        manifest["comparison"] = {
            "data_kind": "seeded demonstration data",
            "seed": SEED,
            "generator": "numpy.random.default_rng",
            "numpy_version": np.__version__,
            "matplotlib_version": mpl.__version__,
            "samples_per_curve": len(time),
            "source_data": data.name,
            "baseline": baseline_fonts,
            "checks": checks,
            "caption": CAPTION,
        }
        Path(str(stem) + ".manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
        )
        Path(str(stem) + ".caption.md").write_text(
            CAPTION + "\n\n"
            "The reference is a synthetic sinusoidal signal; the observation adds "
            "Gaussian noise with seed 19 and standard deviation 0.11. "
            "Both panels contain the same two arrays, linear scales, limits, ticks, "
            "axis labels and legend entries. The left panel uses Matplotlib defaults; "
            "the right uses ohmyplt fonts, colors, line weights and axis styling.\n",
            encoding="utf8",
        )
        plt.close(fig)
    print(str(stem) + ".pdf")


if __name__ == "__main__":
    main()
