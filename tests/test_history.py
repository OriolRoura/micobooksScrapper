import tempfile
import unittest
from pathlib import Path

from micobooks_scraper.history import HistoryStore, canonical_isbn


class HistoryStoreTests(unittest.TestCase):
    def test_canonicalizes_978_isbn13(self) -> None:
        self.assertEqual(canonical_isbn("978-84-9759-318-2"), "8497593189")

    def test_add_and_update_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / "books.json")
            record = store.add(
                "9788497593182",
                title="A book",
                seller_profit=0.28,
                found=True,
            )

            updated = store.set_sell_decision(record["id"], "sell")

            self.assertEqual(updated["sell_decision"], "sell")
            self.assertEqual(store.all()[0]["isbn"], "9788497593182")

    def test_missing_decision_record_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / "books.json")

            with self.assertRaises(KeyError):
                store.set_sell_decision("missing", "not_sell")

    def test_does_not_add_equivalent_isbn_twice(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / "books.json")
            first = store.add("9788497593182", found=False)
            second = store.add("8497593189", title="A book", seller_profit=0.28, found=True)

            self.assertEqual(first["id"], second["id"])
            self.assertEqual(len(store.all()), 1)
            self.assertTrue(store.all()[0]["found"])


if __name__ == "__main__":
    unittest.main()
