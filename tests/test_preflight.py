"""Inspect actual PDF resources before claiming all-vector, embedded-font output."""
from pathlib import Path
import sys
import unittest

from matplotlib import font_manager
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from preflight import inspect_resources


class PdfResourceTests(unittest.TestCase):
    def test_vector_page_and_embedded_font(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.draw_line((20, 20), (150, 20))
            font = font_manager.findfont("DejaVu Sans")
            page.insert_font(fontname="body", fontfile=font)
            page.insert_text((20, 50), "Vector labels", fontname="body")
            images, fonts = inspect_resources(document)
            self.assertEqual(images, [])
            self.assertTrue(fonts)
            self.assertTrue(all(font["embedded"] for font in fonts))

    def test_pdf_container_does_not_hide_a_raster_image(self):
        with pymupdf.open() as document:
            page = document.new_page()
            image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 2, 3), False)
            image.clear_with(255)
            page.insert_image(pymupdf.Rect(20, 20, 60, 80), pixmap=image)
            images, _ = inspect_resources(document)
            self.assertEqual(len(images), 1)
            self.assertEqual((images[0]["width"], images[0]["height"]), (2, 3))

    def test_standard_pdf_font_is_reported_as_unembedded(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((20, 50), "Standard font")
            _, fonts = inspect_resources(document)
            self.assertTrue(fonts)
            self.assertFalse(fonts[0]["embedded"])


if __name__ == "__main__":
    unittest.main()
