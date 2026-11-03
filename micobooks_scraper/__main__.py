"""Command-line entry point for the Micobooks scraper."""

from __future__ import annotations

import os

from .client import MicobooksClient


DEFAULT_ISBN = "9788497593182"


def main() -> None:
    isbn = os.getenv("ISBN", DEFAULT_ISBN)
    quote = MicobooksClient().get_quote(isbn)
    print(f"Title: {quote.title}")
    print(f"ISBN: {quote.isbn or isbn}")
    print(f"Seller profit: {quote.seller_profit:.2f} EUR")


if __name__ == "__main__":
    main()
