"""Exercise first-run errors and the lightweight default workflow."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "quickstart.py"


class QuickstartArguments(unittest.TestCase):
    def test_default_renders_one_data_plot_without_full_pdf_audits(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "figures"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--portable", "--out", str(out)],
                cwd=directory, capture_output=True, text=True, check=True, timeout=60,
            )
            self.assertEqual([p.name for p in out.glob("*.pdf")], ["simple-plot.pdf"])
            self.assertFalse((out / "qa").exists())
            self.assertFalse((out / "network.pdf").exists())
            summary = json.loads((out / "quickstart.json").read_text(encoding="utf8"))
            self.assertEqual(summary["preflight"], "not requested")

    def test_conflicting_font_choices_stop_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "figures"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--portable", "--body-font", "Arial", "--out", str(out)],
                cwd=directory, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Choose --portable or explicit", result.stderr)
            self.assertFalse(out.exists())

    def test_unprepared_interpreter_gets_its_own_install_command(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-S", str(SCRIPT), "--portable"],
                cwd=directory, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Missing Python dependencies:", result.stderr)
            self.assertIn(sys.executable, result.stderr)
            self.assertIn("-m pip install -r", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((Path(directory) / "output").exists())


if __name__ == "__main__":
    unittest.main()
