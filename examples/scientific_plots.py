"""Readable Matplotlib recipes for four seeded synthetic scientific datasets."""
import argparse
import math
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ohmyplt import BLUE, RUST, INK, configure, apply_chart_style, export
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.ticker import FormatStrFormatter


def weighted_linear_fit(x, y, sigma):
    """Fit y = intercept + slope*x with known independent 1-sigma errors."""
    x, y, sigma = [np.asarray(a, dtype=float) for a in (x, y, sigma)]
    if x.ndim != 1 or x.size < 3 or x.shape != y.shape or x.shape != sigma.shape:
        raise ValueError("x, y and sigma must have the same 1-D shape with at least 3 points.")
    if not all(np.isfinite(a).all() for a in (x, y, sigma)):
        raise ValueError("x, y and sigma must be finite.")
    if np.any(sigma <= 0):
        raise ValueError("sigma must be positive.")
    design = np.column_stack((np.ones_like(x), x))
    whitened = design / sigma[:, None]
    if np.linalg.matrix_rank(whitened) < 2:
        raise ValueError("The fit needs at least two distinct x values.")
    coefficients = np.linalg.lstsq(whitened, y / sigma, rcond=None)[0]
    covariance = np.linalg.inv(whitened.T @ whitened)
    residual = y - design @ coefficients
    chi_square = float(np.sum((residual / sigma) ** 2))
    return coefficients, covariance, residual, chi_square


def calibration_data(seed=17):
    rng = np.random.default_rng(seed)
    energy = np.array([59.5, 122.1, 356.0, 511.0, 661.7, 1173.2, 1332.5])
    sigma = np.array([0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 1.7])
    channel = 8 + 1.48 * energy + rng.normal(0, sigma)
    coefficients, covariance, residual, chi_square = weighted_linear_fit(energy, channel, sigma)
    return dict(energy=energy, channel=channel, sigma=sigma, coefficients=coefficients,
                covariance=covariance, residual=residual, chi_square=chi_square, seed=seed)


def spectrum_data(seed=23):
    rng = np.random.default_rng(seed)
    edges = np.linspace(0, 1500, 151)
    centers = (edges[:-1] + edges[1:]) / 2
    expected = 8 + 30 * np.exp(-centers / 600)
    for mean, width, total in [(661.7, 24, 1800), (1173.2, 32, 950)]:
        cdf = np.array([0.5 * (1 + math.erf((e - mean) / (math.sqrt(2) * width)))
                        for e in edges])
        expected += total * np.diff(cdf)
    counts = rng.poisson(expected)
    return dict(edges=edges, centers=centers, counts=counts,
                count_sigma=np.sqrt(counts), expected_counts=expected, seed=seed)


def heatmap_data(seed=29):
    rng = np.random.default_rng(seed)
    x_edges = np.linspace(-2, 2, 81)
    y_edges = np.linspace(-1, 1, 41)
    x = (x_edges[:-1] + x_edges[1:]) / 2
    y = (y_edges[:-1] + y_edges[1:]) / 2
    xx, yy = np.meshgrid(x, y)
    reference = (1.1 * np.exp(-((xx + 0.65)**2 / 0.5 + (yy - 0.12)**2 / 0.24))
                 + 0.6 * np.exp(-((xx - 0.9)**2 / 0.3 + (yy + 0.3)**2 / 0.16)))
    noise = rng.normal(0, 0.015, reference.shape)
    for _ in range(3):
        padded = np.pad(noise, 1, mode="edge")
        noise = (padded[1:-1, 1:-1] + padded[:-2, 1:-1] + padded[2:, 1:-1]
                 + padded[1:-1, :-2] + padded[1:-1, 2:]) / 5
    prediction = reference + 0.06 * np.sin(1.8 * xx) * np.cos(2 * yy) + noise
    return dict(x_edges=x_edges, y_edges=y_edges, reference=reference,
                prediction=prediction, error=prediction-reference, seed=seed)


def distribution_data(seed=31):
    rng = np.random.default_rng(seed)
    return dict(case_id=np.arange(24), group_a=rng.normal(0.12, 0.025, 24),
                group_b=rng.normal(0.15, 0.030, 24), seed=seed)


def calibration_plot():
    data = calibration_data()
    x, y, sigma = (data[k] for k in ("energy", "channel", "sigma"))
    intercept, slope = data["coefficients"]
    fig, (ax, residual_ax) = plt.subplots(
        2, 1, sharex=True, figsize=(85 / 25.4, 96 / 25.4),
        gridspec_kw={"height_ratios": [2.6, 1]}, layout="constrained")
    line_x = np.linspace(0, 1400, 200)
    ax.plot(line_x, intercept + slope * line_x, color=RUST, lw=0.85, label="Weighted fit")
    ax.errorbar(x, y, yerr=sigma, fmt="o", ms=3, color=BLUE, capsize=2,
                lw=0.7, label="Observations")
    ax.set(ylabel="Channel", xlim=(0, 1400))
    ax.set_title("Synthetic calibration", loc="left", fontsize=8)
    ax.legend(loc="upper left", frameon=False, fontsize=6.5)
    residual_ax.axhline(0, color="#8799A3", lw=0.6, ls="--")
    residual_ax.errorbar(x, data["residual"], yerr=sigma, fmt="o", ms=3,
                         color=BLUE, capsize=2, lw=0.7)
    residual_ax.set(xlabel="Energy (keV)", ylabel="Residual\n(channel)", xticks=[0, 500, 1000])
    error = np.sqrt(np.diag(data["covariance"]))
    caption = (
        "Seeded synthetic calibration (seed 17). Seven channel observations are drawn "
        "from 8 + 1.48E with independent Gaussian errors. Bars are known 1-sigma "
        "observation uncertainties. A weighted linear fit minimizes sum[(y-fit)/sigma]^2. "
        f"Intercept = {intercept:.4f} +/- {error[0]:.4f} channels; "
        f"slope = {slope:.6f} +/- {error[1]:.6f} channels/keV; "
        f"chi-square = {data['chi_square']:.4f} with {len(x)-2} degrees of freedom. "
        "Parameter uncertainties use (X^T W X)^-1 with known absolute sigma. "
        "The lower panel shows observation minus fitted value with the same observation bars.\n")
    return fig, data, caption


def spectrum_plot():
    data = spectrum_data()
    fig, ax = plt.subplots(figsize=(85 / 25.4, 70 / 25.4), layout="constrained")
    ax.stairs(data["counts"], data["edges"], color=BLUE, lw=0.8, label="Observed counts")
    ax.errorbar(data["centers"], data["counts"], yerr=data["count_sigma"],
                fmt="none", color=BLUE, lw=0.45, alpha=0.65)
    ax.stairs(data["expected_counts"], data["edges"], color=RUST, ls="--", lw=0.8,
              label="Generating expectation")
    ax.set(xlabel="Energy (keV)", ylabel="Counts / bin", xlim=(0, 1500),
           ylim=(0, 1.35 * np.max(data["counts"] + data["count_sigma"])),
           xticks=[0, 500, 1000, 1500])
    ax.set_title("Synthetic count spectrum", loc="left", fontsize=8)
    ax.legend(loc="upper right", frameon=False, fontsize=6)
    caption = (
        "Seeded synthetic count spectrum (seed 23). Each of 150 bins spans 10 keV. "
        "Counts are independent Poisson draws from the dashed expectation: "
        "an exponential continuum plus Gaussian peaks centered at 661.7 and 1173.2 keV "
        "with widths 24 and 32 keV and expected peak totals 1800 and 950. "
        "Peak expectations are integrated over bin edges. Stair heights are counts per bin; "
        "bars at arithmetic bin centers show the plug-in Poisson standard deviation sqrt(N).\n")
    return fig, data, caption


def heatmap_plot():
    data = heatmap_data()
    fig, axes = plt.subplots(1, 3, sharex=True, sharey=True,
                             figsize=(183 / 25.4, 62 / 25.4), layout="constrained")
    common_min = min(data["reference"].min(), data["prediction"].min())
    common_max = max(data["reference"].max(), data["prediction"].max())
    common = Normalize(common_min, common_max)
    error_max = float(np.max(np.abs(data["error"])))
    error_norm = TwoSlopeNorm(vmin=-error_max, vcenter=0, vmax=error_max)
    for ax, key, title in zip(axes, ["reference", "prediction", "error"],
                              ["Reference", "Prediction", "Prediction - reference"]):
        image = ax.pcolormesh(data["x_edges"], data["y_edges"], data[key],
                              norm=error_norm if key == "error" else common,
                              cmap="RdBu_r" if key == "error" else "viridis", rasterized=True)
        ax.set_aspect("equal")
        ax.set(xlabel=r"$x$ (mm)", xticks=[-2, 0, 2], yticks=[-1, 0, 1])
        ax.set_title(title, fontsize=7.5)
        if key == "prediction":
            common_image = image
    axes[0].set_ylabel(r"$y$ (mm)")
    bar = fig.colorbar(common_image, ax=axes[:2], location="bottom", pad=0.12,
                       fraction=0.12, ticks=np.linspace(common_min, common_max, 3))
    bar.set_label("Amplitude (a.u.)")
    error_bar = fig.colorbar(image, ax=axes[2], location="bottom", pad=0.12,
                             fraction=0.12, ticks=[-error_max, 0, error_max])
    error_bar.set_label("Signed error (a.u.)")
    for colorbar in (bar, error_bar):
        colorbar.ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    fig.suptitle("Seeded synthetic spatial field", fontsize=8)
    data.update(common_limits=np.array([common_min, common_max]),
                error_limits=np.array([-error_max, error_max]))
    caption = (
        "Seeded synthetic spatial fields (seed 29), sampled on an 80 x 40 grid covering "
        "x = [-2, 2] mm and y = [-1, 1] mm. Equal aspect preserves the 2:1 geometry. "
        "The reference is a sum of two Gaussian fields; the prediction adds a smooth "
        "sinusoidal perturbation and seeded spatial noise. Reference and prediction "
        f"share one amplitude scale [{common_min:.5f}, {common_max:.5f}]. "
        "Signed error is prediction minus reference, with an independent, zero-centered "
        f"diverging scale [{-error_max:.5f}, {error_max:.5f}].\n")
    return fig, data, caption


def distribution_plot():
    data = distribution_data()
    rng = np.random.default_rng(32)
    fig, ax = plt.subplots(figsize=(85 / 25.4, 72 / 25.4), layout="constrained")
    groups = [data["group_a"], data["group_b"]]
    boxes = ax.boxplot(groups, positions=[1, 2], widths=0.42, patch_artist=True,
                       showfliers=False, medianprops={"color": INK, "lw": 0.9},
                       whiskerprops={"color": "#758A95", "lw": 0.7},
                       capprops={"color": "#758A95", "lw": 0.7})
    for i, (values, color, fill) in enumerate(zip(groups, [BLUE, RUST], ["#E5F0F2", "#F6E7DB"]), 1):
        boxes["boxes"][i-1].set(facecolor=fill, edgecolor=color, linewidth=0.7)
        ax.scatter(i + rng.uniform(-0.11, 0.11, len(values)), values, s=10,
                    facecolor="white", edgecolor=color, linewidth=0.7, zorder=3)
    ax.set(xticks=[1, 2], xticklabels=["Group A", "Group B"],
           ylabel="Response (a.u.)", xlim=(0.5, 2.5))
    ax.set_title("Independent synthetic cases", loc="left", fontsize=8)
    caption = (
        "Seeded synthetic distributions (seed 31): 24 independent cases in each group. "
        "Group A draws from Normal(0.12, 0.025^2) and Group B from Normal(0.15, 0.030^2). "
        "Each dot is one case; horizontal jitter (seed 32) only separates dots. "
        "Boxes show the 25th to 75th percentiles and median; whiskers extend to the "
        "most extreme values within 1.5 IQR of the box. All cases, including outliers, "
        "remain visible as dots. Groups are independent.\n")
    return fig, data, caption


RECIPES = {"calibration": calibration_plot, "spectrum": spectrum_plot,
           "heatmap": heatmap_plot, "distribution": distribution_plot}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=[*RECIPES, "all"], default="all")
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--body-font", default="Arial")
    parser.add_argument("--math-font", default="Times New Roman")
    parser.add_argument("--font-dir")
    args = parser.parse_args()
    configure(args.body_font, args.math_font, args.font_dir)
    args.out.mkdir(parents=True, exist_ok=True)
    kinds = list(RECIPES) if args.kind == "all" else [args.kind]
    for kind in kinds:
        fig, arrays, caption = RECIPES[kind]()
        for index, ax in enumerate(fig.axes):
            apply_chart_style(ax, boxed=kind == "heatmap" and index < 3)
        data = args.out / f"{kind}-data.npz"
        np.savez_compressed(data, **arrays)
        export(fig, args.out / kind, source_files=[__file__, data])
        (args.out / f"{kind}.caption.md").write_text(caption, encoding="utf8")
        plt.close(fig)
        print(args.out / f"{kind}.pdf")


if __name__ == "__main__":
    main()
