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
from ohmyplt import apply_chart_style, configure, export
import matplotlib.pyplot as plt


class ChartStyleTests(unittest.TestCase):
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
