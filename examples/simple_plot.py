"""A single-column curve and error-bar plot using ordinary Matplotlib axes."""
import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ohmyplt import configure, apply_chart_style, export, get_palette
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--body-font", default="Arial")
    parser.add_argument("--math-font", default="Times New Roman")
    parser.add_argument("--font-dir")
    args = parser.parse_args()
    configure(args.body_font, args.math_font, args.font_dir)

    rng = np.random.default_rng(41)
    x = np.linspace(0, 10, 11)
    sigma = 0.055 + 0.004 * x
    y = 0.3 + 1.6 * (1 - np.exp(-x / 3)) + rng.normal(0, sigma)
    curve_x = np.linspace(0, 10, 300)
    curve_y = 0.3 + 1.6 * (1 - np.exp(-curve_x / 3))

    observation_color, _, curve_color = get_palette("contrast")
    fig, ax = plt.subplots(figsize=(85 / 25.4, 56 / 25.4), layout="constrained")
    ax.plot(curve_x, curve_y, color=curve_color, lw=1.05,
            label="Generating curve", zorder=2)
    ax.errorbar(x, y, yerr=sigma, fmt="o", ms=3.6, capsize=2, lw=0.7,
                color=observation_color, ecolor="#A8BED4", markeredgecolor="white",
                markeredgewidth=0.45, label="Observations", zorder=3)
    ax.set(xlabel=r"Input $x$ (a.u.)", ylabel=r"Response $y$ (a.u.)",
           xlim=(-0.3, 10.3), ylim=(0, 2.2), xticks=[0, 5, 10])
    ax.legend(loc="lower right", frameon=False, fontsize=6.5)
    apply_chart_style(ax)

    args.out.mkdir(parents=True, exist_ok=True)
    data = args.out / "simple-plot-data.npz"
    np.savez_compressed(data, x=x, y=y, sigma=sigma, curve_x=curve_x,
                        curve_y=curve_y, seed=41)
    export(fig, args.out / "simple-plot", source_files=[__file__, data])
    (args.out / "simple-plot.caption.md").write_text(
        "Seeded synthetic response (seed 41). Eleven observations are drawn from "
        "y = 0.3 + 1.6[1 - exp(-x/3)] with independent Gaussian noise. Error bars "
        "are the known one-standard-deviation observation uncertainties, "
        "sigma = 0.055 + 0.004x. The line is the generating curve.\n",
        encoding="utf8",
    )
    plt.close(fig)
    print(args.out / "simple-plot.pdf")


if __name__ == "__main__":
    main()
