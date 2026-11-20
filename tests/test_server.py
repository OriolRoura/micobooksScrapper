import unittest
from unittest.mock import patch

from micobooks_scraper.server import build_parser


class ServerOptionsTests(unittest.TestCase):
    def test_lan_only_is_the_default_policy(self) -> None:
        options = build_parser().parse_args([])

        self.assertFalse(options.allow_public_access)

    def test_public_access_requires_explicit_flag(self) -> None:
        options = build_parser().parse_args(["--allow-public-access"])

        self.assertTrue(options.allow_public_access)

    @patch("micobooks_scraper.server.validate_tesseract", side_effect=RuntimeError("Tesseract missing"))
    @patch("micobooks_scraper.server.uvicorn.run")
    @patch("micobooks_scraper.server.Path.is_file", return_value=True)
    def test_startup_reports_missing_tesseract(
        self,
        _is_file,
        _run,
        _validate_tesseract,
    ) -> None:
        with patch("sys.argv", ["micobooks-server"]):
            with self.assertRaises(SystemExit) as error:
                from micobooks_scraper.server import main

                main()

        self.assertIn("Tesseract missing", str(error.exception))
        _run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
