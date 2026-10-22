"""Paired cases and a time forecast on standard Matplotlib subplots."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ohmyplt import configure, apply_chart_style, check_axes_alignment, export, BLUE, RUST
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--body-font", default="Arial")
    parser.add_argument("--math-font", default="Times New Roman")
    parser.add_argument("--font-dir")
    args = parser.parse_args()
    configure(args.body_font, args.math_font, args.font_dir)
    rng = np.random.default_rng(19)
    reference = np.linspace(0.07, 0.15, 12) + rng.normal(0, 0.006, 12)
    model = 0.8 * reference + rng.normal(0, 0.008, 12)
    t = np.linspace(0, 30, 121)
    truth = np.sin(t / 3) + 0.15 * np.cos(t / 1.5)
    forecast = truth + 0.1 * np.sin(t / 2 + 0.3)
    obs = np.arange(0, 49, 8)

    fig, (a, b) = plt.subplots(1, 2, figsize=(183 / 25.4, 78 / 25.4),
                               layout="constrained")
    for r, m in zip(reference, model):
        a.plot([0, 1], [r, m], color="#B6C4CC", lw=0.65, zorder=1)
    a.scatter(np.zeros(12), reference, s=13, color=BLUE, zorder=2)
    a.scatter(np.ones(12), model, s=13, color=RUST, zorder=2)
    a.set(xlim=(-0.3, 1.3), xticks=[0, 1], xticklabels=["Reference", "Model"],
          ylabel=r"Error $(\%)$")
    a.set_title("a  Paired cases", loc="left", fontsize=8, weight="bold", pad=26)

    b.plot(t, truth, color="#9AAAB4", lw=0.8, label="Reference")
    keep = t >= 12
    b.plot(t[keep], forecast[keep], color=RUST, lw=1, label="Forecast")
    b.scatter(t[obs], truth[obs], s=10, facecolors="white", edgecolors=BLUE,
              linewidths=0.7, label="Samples", zorder=3)
    b.axvline(12, color="#AAB7BF", lw=0.6, ls="--")
    b.set(xlim=(0, 30), xticks=[0, 10, 20, 30], xlabel=r"$t\;(\mathrm{h})$",
          ylabel=r"$s(t)$")
    b.set_title("b  Time forecast", loc="left", fontsize=8, weight="bold", pad=26)
    b.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=3,
             fontsize=6.5, frameon=False, columnspacing=0.9, handlelength=1.2)
    for ax in (a, b):
        apply_chart_style(ax)

    args.out.mkdir(parents=True, exist_ok=True)
    data = args.out / "data-demo.npz"
    np.savez_compressed(data, reference=reference, model=model, t=t, truth=truth,
                        forecast=forecast, sample_indices=obs, forecast_start=12, seed=19)
    alignment = check_axes_alignment(fig, [a, b])
    (args.out / "data-plot.alignment.json").write_text(
        json.dumps(alignment, indent=2) + "\n", encoding="utf8"
    )
    if not alignment["passed"]:
        raise RuntimeError("Comparable plotting rectangles differ.")
    export(fig, args.out / "data-plot", source_files=[__file__, data])
    (args.out / "data-plot.caption.md").write_text(
        "Seeded synthetic examples (seed 19). Left: twelve independent cases, "
        "each with a paired Reference and Model error expressed in percent; "
        "a line connects the same case. Right: a synthetic reference signal, "
        "seven exact history samples through t = 12 h, and a perturbed future "
        "curve shown from t = 12 h. The dashed line marks the forecast origin.\n",
        encoding="utf8",
    )
    plt.close(fig)
    print(args.out / "data-plot.pdf")


if __name__ == "__main__":
    main()
