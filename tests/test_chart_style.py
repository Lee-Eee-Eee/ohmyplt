"""Plot styling must preserve scientific meaning and the selected backend."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from ohmyplt import BLUE, RUST, apply_chart_style, configure, export, get_palette
import matplotlib as mpl
import matplotlib.pyplot as plt


class ChartStyleTests(unittest.TestCase):
    def test_palette_limits_reject_repeated_and_invalid_color_requests(self):
        self.assertEqual(get_palette("contrast"), ["#004488", "#DDAA33", "#BB5566"])
        self.assertEqual(len(get_palette("bright")), 7)
        self.assertEqual(len(get_palette("okabe-ito")), 8)
        for name in ("contrast", "bright", "okabe-ito"):
            colors = get_palette(name)
            self.assertEqual(len(colors), len(set(colors)))
            self.assertEqual(get_palette(name, 2), colors[:2])
            for n in (0, -1, len(colors) + 1):
                with self.subTest(name=name, n=n), self.assertRaises(ValueError):
                    get_palette(name, n)
        with self.assertRaisesRegex(ValueError, "Unknown palette"):
            get_palette("unknown")
        with self.assertRaisesRegex(TypeError, "integer"):
            get_palette("contrast", 2.5)

    def test_configure_keeps_positional_fonts_and_explicit_colors(self):
        with mpl.rc_context():
            configure("DejaVu Sans", "DejaVu Serif", None, palette="bright")
            fig, ax = plt.subplots()
            auto_line, = ax.plot([0, 1], [0, 1])
            blue_line, = ax.plot([0, 1], [1, 2], color=BLUE)
            rust_line, = ax.plot([0, 1], [2, 3], color=RUST)
            self.assertEqual(auto_line.get_color(), get_palette("bright")[0])
            self.assertEqual(blue_line.get_color(), BLUE)
            self.assertEqual(rust_line.get_color(), RUST)
            plt.close(fig)

    def test_chart_style_preserves_explicit_fallback_for_text_ticks(self):
        with mpl.rc_context():
            configure("DejaVu Sans", "DejaVu Serif", fallback_fonts=("DejaVu Serif",))
            fig, ax = plt.subplots()
            ax.set_xticks([0, 1], ["Alpha", "Beta"])
            ax.set_yticks([0, 1])
            apply_chart_style(ax)
            self.assertEqual(ax.get_xticklabels()[0].get_fontfamily(),
                             ["DejaVu Sans", "DejaVu Serif"])
            self.assertEqual(ax.get_yticklabels()[0].get_fontfamily(), ["DejaVu Serif"])
            self.assertEqual(ax.xaxis.label.get_fontfamily(),
                             ["DejaVu Sans", "DejaVu Serif"])
            plt.close(fig)

    def test_unavailable_fallback_font_fails_explicitly(self):
        with self.assertRaisesRegex(RuntimeError, "Font unavailable: Missing Test Family"):
            configure("DejaVu Sans", "DejaVu Serif",
                      fallback_fonts=("Missing Test Family 12345",))

    def test_style_preserves_data_scale_units_and_spatial_aspect(self):
        configure("DejaVu Sans", "DejaVu Serif")
        fig, ax = plt.subplots()
        x, y = np.array([1, 10, 100]), np.array([0.2, 0.5, 0.8])
        line, = ax.plot(x, y)
        ax.set(xscale="log", xlim=(1, 100), ylim=(0, 1), xlabel="Energy (keV)", ylabel="Efficiency")
        ax.set_aspect(2)
        apply_chart_style(ax, boxed=True)
        np.testing.assert_array_equal(line.get_xdata(), x)
        np.testing.assert_array_equal(line.get_ydata(), y)
        self.assertEqual(ax.get_xscale(), "log")
        self.assertEqual(ax.get_xlim(), (1, 100))
        self.assertEqual(ax.get_ylim(), (0, 1))
        self.assertEqual(ax.get_xlabel(), "Energy (keV)")
        self.assertEqual(ax.get_ylabel(), "Efficiency")
        self.assertEqual(ax.get_aspect(), 2)
        self.assertTrue(all(spine.get_visible() for spine in ax.spines.values()))
        plt.close(fig)

    def test_png_only_delivery_does_not_create_other_formats(self):
        configure("DejaVu Sans", "DejaVu Serif")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [1, 2])
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "requested"
            export(fig, stem, formats=("png",), dpi=90)
            self.assertTrue(stem.with_suffix(".png").is_file())
            self.assertFalse(stem.with_suffix(".pdf").exists())
            self.assertFalse(stem.with_suffix(".svg").exists())
            manifest = json.loads(stem.with_suffix(".manifest.json").read_text(encoding="utf8"))
            self.assertEqual(manifest["formats"], ["png"])
        plt.close(fig)

    def test_import_keeps_an_existing_backend(self):
        code = (
            "import matplotlib; matplotlib.use('svg'); "
            f"import sys; sys.path.insert(0, {str(SCRIPTS)!r}); "
            "import ohmyplt; print(matplotlib.get_backend())"
        )
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip().lower(), "svg")

    def test_svg_keeps_labels_as_editable_text(self):
        configure("DejaVu Sans", "DejaVu Serif")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [1, 2])
        ax.set(xlabel="Energy (keV)", ylabel="Counts / bin")
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "editable"
            export(fig, stem, formats=("svg",))
            root = ET.parse(stem.with_suffix(".svg")).getroot()
            labels = ["".join(node.itertext()) for node in root.iter("{http://www.w3.org/2000/svg}text")]
            self.assertIn("Energy (keV)", labels)
            self.assertIn("Counts / bin", labels)
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
