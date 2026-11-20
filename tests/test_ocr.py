import unittest
from unittest.mock import patch

from micobooks_scraper.ocr import OcrConfig, OcrError, _is_valid_isbn, extract_barcode_candidates, extract_isbn_candidates


class OcrTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_standard_ocr_configuration_preserves_defaults(self) -> None:
        self.assertEqual(
            OcrConfig.from_environment(),
            OcrConfig(profile="standard", preprocess_scale=2.0, max_dimension=None, max_workers=4),
        )

    @patch.dict("os.environ", {"MICOBOOKS_OCR_PROFILE": "raspberry-pi"}, clear=True)
    def test_raspberry_pi_profile_uses_bounded_defaults(self) -> None:
        self.assertEqual(
            OcrConfig.from_environment(),
            OcrConfig(profile="raspberry-pi", preprocess_scale=1.0, max_dimension=2048, max_workers=1),
        )

    @patch.dict("os.environ", {"MICOBOOKS_OCR_MAX_WORKERS": "0"}, clear=True)
    def test_ocr_configuration_rejects_invalid_worker_limit(self) -> None:
        with self.assertRaisesRegex(OcrError, "MICOBOOKS_OCR_MAX_WORKERS"):
            OcrConfig.from_environment()

    @patch("micobooks_scraper.ocr.ThreadPoolExecutor")
    @patch("micobooks_scraper.ocr.extract_barcode_candidates", return_value=[])
    @patch("micobooks_scraper.ocr.ImageOps.autocontrast")
    @patch("micobooks_scraper.ocr.ImageOps.exif_transpose")
    @patch("micobooks_scraper.ocr.Image.open")
    def test_raspberry_pi_profile_enforces_image_and_worker_limits(
        self,
        image_open,
        exif_transpose,
        autocontrast,
        _extract_barcode_candidates,
        executor,
    ) -> None:
        image = image_open.return_value
        exif_transpose.return_value = image
        image.convert.return_value = image
        autocontrast.return_value = image
        image.resize.return_value = image
        image.width = 4000
        image.height = 3000
        executor.return_value.__enter__.return_value.map.return_value = [""] * 5

        extract_isbn_candidates(
            b"image",
            OcrConfig(profile="raspberry-pi", preprocess_scale=1.0, max_dimension=2048, max_workers=1),
        )

        image.resize.assert_called_once_with((2048, 1536), unittest.mock.ANY)
        executor.assert_called_once_with(max_workers=1)

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
