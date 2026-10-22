"""A conceptual two-channel optical measurement with editable native geometry."""

import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ohmyplt import configure, export
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import (
    Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle,
)
from matplotlib.path import Path as MplPath


COLORS = {
    "ink": "#243445", "muted": "#566577", "outline": "#496171",
    "optic": "#C98613", "optic_light": "#EDB748", "data": "#2F638F",
    "glass": "#E9F4F5", "glass_edge": "#6D959C",
    "sample": "#66AFA4", "sample_edge": "#31776F",
    "metal": "#E9EDF1", "metal_side": "#D5DEE7", "aperture": "#344B5E",
    "process_fill": "#EDF4F9", "process_edge": "#527C9D",
}

CAPTION = (
    "Conceptual arrangement for two-channel optical transmittance measurement. "
    "The beam splitter sends one optical path through the sample to the signal "
    "detector (S), while the other reaches the reference detector (R). Solid "
    "amber arrows show optical paths; dashed blue arrows show readout data. "
    "Transmittance is normalized as T = (S/R)/(S0/R0). All readings are "
    "dark-corrected, and S0/R0 is the baseline ratio acquired in the reference "
    "state with the sample removed. This normalization assumes a stable source "
    "spectral shape and relative channel response, with linear detector "
    "response across sample and reference measurements. "
    "Component sizes, spacing, and ray widths are schematic.\n"
)


def label(ax, x, y, text, *, size=9.0, weight="normal", color=None,
          ha="center", **kwargs):
    return ax.text(x, y, text, fontsize=size, fontweight=weight,
                   color=color or COLORS["ink"], ha=ha, va="center",
                   zorder=12, **kwargs)


def rounded_path(points, radius=2.0):
    """Route continuously through orthogonal corners, tangent to each segment."""
    points = [np.asarray(p, dtype=float) for p in points]
    vertices, codes = [points[0]], [MplPath.MOVETO]
    for a, p, b in zip(points[:-2], points[1:-1], points[2:]):
        vin, vout = a - p, b - p
        distance = min(radius, np.linalg.norm(vin) / 2, np.linalg.norm(vout) / 2)
        start = p + vin / np.linalg.norm(vin) * distance
        end = p + vout / np.linalg.norm(vout) * distance
        vertices.extend([start, p, end])
        codes.extend([MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3])
    vertices.append(points[-1])
    codes.append(MplPath.LINETO)
    return MplPath(vertices, codes)


def reading(ax, points):
    """Readout data end at detector and processing-block boundaries."""
    ax.add_patch(FancyArrowPatch(
        path=rounded_path(points), arrowstyle="-|>", mutation_scale=8,
        linewidth=1.35, linestyle=(0, (3.5, 2.6)), color=COLORS["data"],
        capstyle="round", joinstyle="round", zorder=8,
    ))


def beam(ax, p0, p1, *, arrow=True, position=0.63):
    """Directional optical ray; width does not encode measured intensity."""
    ax.add_line(Line2D(*zip(p0, p1), color=COLORS["optic_light"], alpha=0.13,
                       linewidth=4.8, solid_capstyle="round", zorder=4))
    ax.add_line(Line2D(*zip(p0, p1), color=COLORS["optic"], linewidth=1.65,
                       solid_capstyle="round", zorder=5))
    if arrow:
        a, b = np.asarray(p0, float), np.asarray(p1, float)
        direction = (b - a) / np.linalg.norm(b - a)
        end = a + position * (b - a)
        ax.add_patch(FancyArrowPatch(
            end - direction * 3.0, end, arrowstyle="-|>", mutation_scale=8.3,
            linewidth=1.65, shrinkA=0, shrinkB=0, color=COLORS["optic"], zorder=6,
        ))


def build_figure():
    """Use mm figure coordinates, independent of unspecified apparatus sizes."""
    fig = plt.figure(figsize=(183 / 25.4, 82 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 183), ylim=(14, 96), aspect="equal")
    ax.axis("off")

    # Neutral cylindrical source: no emitter technology is implied.
    ax.add_patch(Rectangle((9.3, 41.4), 11.3, 9.2, facecolor=COLORS["metal"],
                           edgecolor=COLORS["outline"], linewidth=0.85, zorder=7))
    ax.add_patch(Ellipse((9.3, 46), 3.0, 9.2, facecolor=COLORS["metal_side"],
                         edgecolor=COLORS["outline"], linewidth=0.85, zorder=8))
    ax.add_patch(Ellipse((20.6, 46), 3.0, 9.2, facecolor="#F5E4BF",
                         edgecolor=COLORS["outline"], linewidth=0.85, zorder=8))
    ax.add_patch(Ellipse((21.15, 46), 1.2, 5.1, facecolor=COLORS["optic_light"],
                         edgecolor=COLORS["optic"], linewidth=0.65, zorder=9))
    label(ax, 15.7, 33.2, "Light source")

    # The diagonal coating reflects the +x input toward the +y reference arm.
    x0, x1, y0, y1, depth = 41.5, 52.5, 40.5, 51.5, 2.2
    ax.add_patch(Polygon(
        [(x0, y1), (x0 + depth, y1 + depth),
         (x1 + depth, y1 + depth), (x1, y1)],
        facecolor="#F5FAFA", edgecolor=COLORS["glass_edge"],
        linewidth=0.65, zorder=2,
    ))
    ax.add_patch(Polygon(
        [(x1, y0), (x1 + depth, y0 + depth),
         (x1 + depth, y1 + depth), (x1, y1)],
        facecolor="#D9EBED", edgecolor=COLORS["glass_edge"],
        linewidth=0.65, zorder=2,
    ))
    ax.add_patch(Rectangle((x0, y0), 11, 11, facecolor=COLORS["glass"],
                           edgecolor=COLORS["glass_edge"], linewidth=0.9, zorder=3))
    ax.add_line(Line2D([x0, x1], [y0, y1], color=COLORS["glass_edge"],
                       linewidth=1.35, zorder=7))
    label(ax, 47, 33.2, "Beam splitter")

    # Sample plate: illustrative thickness with a visible transmitted ray.
    corners = [(80.5, 37.0), (85.2, 38.2), (85.2, 55.2), (80.5, 54.0)]
    ax.add_patch(Polygon(corners, facecolor=COLORS["sample"], alpha=0.22,
                         edgecolor="none", zorder=3))
    ax.add_patch(Polygon(corners, fill=False, edgecolor=COLORS["sample_edge"],
                         linewidth=0.9, zorder=7))
    ax.add_line(Line2D([82, 82], [37.4, 54.4], color=COLORS["sample_edge"],
                       alpha=0.6, linewidth=0.6, zorder=7))
    label(ax, 82.9, 33.2, "Sample")

    # Signal detector: left-facing aperture and right-side readout port.
    ax.add_patch(Rectangle((109, 40), 15, 12, facecolor=COLORS["metal"],
                           edgecolor=COLORS["outline"], linewidth=0.9, zorder=7))
    ax.add_patch(Rectangle((121.6, 40), 2.4, 12, facecolor=COLORS["metal_side"],
                           edgecolor="none", zorder=8))
    ax.add_patch(Rectangle((108, 42), 2.2, 8, facecolor=COLORS["aperture"],
                           edgecolor=COLORS["outline"], linewidth=0.65, zorder=8))
    ax.add_patch(Rectangle((108, 43.4), 0.75, 5.2, facecolor="#ACBDCA",
                           edgecolor="none", zorder=9))
    label(ax, 116.2, 33.2, "Signal detector")

    # Reference detector receives the upward optical branch.
    ax.add_patch(Rectangle((40, 70), 14, 13, facecolor=COLORS["metal"],
                           edgecolor=COLORS["outline"], linewidth=0.9, zorder=7))
    ax.add_patch(Rectangle((40, 80.6), 14, 2.4, facecolor=COLORS["metal_side"],
                           edgecolor="none", zorder=8))
    ax.add_patch(Rectangle((43, 69), 8, 2.2, facecolor=COLORS["aperture"],
                           edgecolor=COLORS["outline"], linewidth=0.65, zorder=8))
    ax.add_patch(Rectangle((44.4, 69), 5.2, 0.75, facecolor="#ACBDCA",
                           edgecolor="none", zorder=9))
    label(ax, 47, 89, "Reference detector")

    # Branch at the splitter coating; the sample intercepts only the signal arm.
    beam(ax, (22, 46), (41.5, 46))
    beam(ax, (41.5, 46), (52.5, 46), arrow=False)
    beam(ax, (47, 46), (47, 51.5), arrow=False)
    beam(ax, (52.5, 46), (80.5, 46), position=0.59)
    beam(ax, (80.5, 46), (85.2, 46), arrow=False)
    beam(ax, (85.2, 46), (108, 46), position=0.64)
    beam(ax, (47, 51.5), (47, 69), position=0.65)
    label(ax, 66, 57.4, "Signal arm", size=8.3, color=COLORS["muted"])
    label(ax, 53, 62, "Reference arm", size=8.3,
          color=COLORS["muted"], ha="left")

    # Ratio operation uses two separate inputs; no additive merge is implied.
    ax.add_patch(FancyBboxPatch(
        (137, 41), 40, 25, boxstyle="round,pad=0,rounding_size=1.5",
        facecolor=COLORS["process_fill"], edgecolor=COLORS["process_edge"],
        linewidth=1.0, zorder=4,
    ))
    label(ax, 157, 59.2, "Normalization", weight="bold")
    label(ax, 157, 49.4, r"$T=(S/R)/(S_0/R_0)$", size=10.5)
    reading(ax, [(54, 77), (157, 77), (157, 66)])
    reading(ax, [(124, 46), (137, 46)])
    label(ax, 62, 81.1, r"$R$", size=11.2, color=COLORS["data"])
    label(ax, 130.5, 51, r"$S$", size=11.2, color=COLORS["data"])
    reading(ax, [(157, 41), (157, 28.7)])
    label(ax, 157, 23.4, r"Transmittance $T$", size=9.6, weight="bold")

    beam(ax, (9, 20.5), (21, 20.5), position=0.70)
    label(ax, 24, 20.5, "Optical path", size=8.3, ha="left")
    reading(ax, [(56, 20.5), (68, 20.5)])
    label(ax, 71, 20.5, "Readout data", size=8.3, ha="left")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--body-font", default="Arial")
    parser.add_argument("--math-font", default="Times New Roman")
    parser.add_argument("--font-dir")
    args = parser.parse_args()
    configure(args.body_font, args.math_font, args.font_dir)

    fig = build_figure()
    stem = args.out / "optical-schematic"
    export(fig, stem, formats=("pdf", "svg", "png"), source_files=[__file__])
    stem.with_suffix(".caption.md").write_text(CAPTION, encoding="utf8")
    plt.close(fig)
    print(stem.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
