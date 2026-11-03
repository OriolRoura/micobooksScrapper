import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from micobooks_scraper.api import app
from micobooks_scraper.client import BookQuote, MicobooksError


class QuoteApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_index(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quote_endpoint"], "POST /api/quote")

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("micobooks_scraper.api.MicobooksClient.get_quote")
    def test_quote_returns_scraped_result(self, get_quote) -> None:
        get_quote.return_value = BookQuote(
            title="A book",
            isbn="8497593189",
            ean="9788497593182",
            seller_profit=0.28,
            image_url=None,
        )

        response = self.client.post("/api/quote", json={"isbn": "9788497593182"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["seller_profit"], 0.28)
        get_quote.assert_called_once_with("9788497593182")

    def test_quote_rejects_short_identifier(self) -> None:
        response = self.client.post("/api/quote", json={"isbn": "123"})

        self.assertEqual(response.status_code, 422)

    @patch("micobooks_scraper.api.extract_isbn_candidates")
    @patch("micobooks_scraper.api.MicobooksClient.get_quote")
    def test_image_quote_extracts_isbn_and_returns_result(self, get_quote, extract_candidates) -> None:
        extract_candidates.return_value = ["9788497593182"]
        get_quote.return_value = BookQuote(
            title="A book",
            isbn="8497593189",
            ean="9788497593182",
            seller_profit=0.28,
            image_url=None,
        )

        response = self.client.post(
            "/api/quote-from-image",
            files={"image": ("book.jpg", b"image", "image/jpeg")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["seller_profit"], 0.28)
        get_quote.assert_called_once_with("9788497593182")

    @patch("micobooks_scraper.api.extract_isbn_candidates")
    @patch("micobooks_scraper.api.MicobooksClient.get_quote")
    def test_image_quote_reports_detected_isbn_when_price_is_missing(self, get_quote, extract_candidates) -> None:
        extract_candidates.return_value = ["9788497593182"]
        get_quote.side_effect = MicobooksError("No quotation found")

        response = self.client.post(
            "/api/quote-from-image",
            files={"image": ("book.jpg", b"image", "image/jpeg")},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("9788497593182", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
