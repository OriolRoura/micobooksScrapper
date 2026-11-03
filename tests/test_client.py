import unittest

from micobooks_scraper.client import MicobooksClient


class MicobooksClientTests(unittest.TestCase):
    def test_normalizes_valid_identifier(self) -> None:
        self.assertEqual(MicobooksClient._normalize_identifier("978-84 9759-3182"), "9788497593182")

    def test_rejects_invalid_identifier(self) -> None:
        with self.assertRaises(ValueError):
            MicobooksClient._normalize_identifier("book")

    def test_selects_matching_item(self) -> None:
        items = [
            {"isbn_identifier": "1111111111", "seller_profit": 1},
            {"isbn_identifier": "8497593189", "seller_profit": 0.28},
        ]
        selected = MicobooksClient._select_item(items, "8497593189")
        self.assertEqual(selected["seller_profit"], 0.28)


if __name__ == "__main__":
    unittest.main()
