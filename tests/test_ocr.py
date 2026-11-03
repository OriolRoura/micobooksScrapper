import unittest
from unittest.mock import patch

from micobooks_scraper.ocr import _is_valid_isbn, extract_barcode_candidates, extract_isbn_candidates


class OcrTests(unittest.TestCase):
    def test_validates_isbn_13(self) -> None:
        self.assertTrue(_is_valid_isbn("9788497593182"))
        self.assertFalse(_is_valid_isbn("9788497593183"))

    def test_validates_isbn_10(self) -> None:
        self.assertTrue(_is_valid_isbn("8497593189"))

    @patch("micobooks_scraper.ocr.zxingcpp.read_barcodes")
    def test_extracts_valid_barcode(self, read_barcodes) -> None:
        read_barcodes.return_value = [type("Barcode", (), {"text": "9788497593182"})()]

        self.assertEqual(extract_barcode_candidates(object()), ["9788497593182"])

    @patch("micobooks_scraper.ocr.pytesseract.image_to_string")
    @patch("micobooks_scraper.ocr.ImageOps.autocontrast")
    @patch("micobooks_scraper.ocr.ImageOps.exif_transpose")
    @patch("micobooks_scraper.ocr.Image.open")
    def test_handles_spaced_and_misread_digits(self, image_open, exif_transpose, autocontrast, image_to_string) -> None:
        image = image_open.return_value
        exif_transpose.return_value = image
        image.convert.return_value = image
        autocontrast.return_value = image
        image.resize.return_value = image
        image.width = 100
        image.height = 100
        image_to_string.return_value = "ISBN 978 O306406157"

        self.assertEqual(extract_isbn_candidates(b"image"), ["9780306406157"])

    @patch("micobooks_scraper.ocr.pytesseract.image_to_string")
    @patch("micobooks_scraper.ocr.ImageOps.autocontrast")
    @patch("micobooks_scraper.ocr.ImageOps.exif_transpose")
    @patch("micobooks_scraper.ocr.Image.open")
    def test_extracts_unique_candidates(self, image_open, exif_transpose, autocontrast, image_to_string) -> None:
        image = image_open.return_value
        exif_transpose.return_value = image
        image.convert.return_value = image
        autocontrast.return_value = image
        image.resize.return_value = image
        image.width = 100
        image.height = 100
        image_to_string.return_value = "ISBN 9788497593182\nISBN 9788497593182"

        self.assertEqual(extract_isbn_candidates(b"image"), ["9788497593182"])


if __name__ == "__main__":
    unittest.main()
