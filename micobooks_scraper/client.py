"""HTTP client for the Micobooks quotation endpoint."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://www.micobooks.com"
ISBN_PATTERN = re.compile(r"^[0-9Xx-]+$")


class MicobooksError(RuntimeError):
    """Raised when Micobooks cannot return a usable quotation."""


@dataclass(frozen=True)
class BookQuote:
    title: str
    isbn: str | None
    ean: str | None
    seller_profit: float
    image_url: str | None = None


class MicobooksClient:
    """Query Micobooks' public quotation endpoint."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_quote(self, isbn: str) -> BookQuote:
        """Return the first matching quotation for an ISBN or EAN."""
        identifier = self._normalize_identifier(isbn)
        query = urlencode({"identifier": identifier, "type_search": "ean"})
        request = Request(
            f"{self.base_url}/quotation/search_items?{query}",
            headers={
                "Accept": "application/json",
                "User-Agent": "micobooks-scraper/0.1",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload: Any = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise MicobooksError(f"Could not query Micobooks: {error}") from error

        items = payload.get("items") if isinstance(payload, dict) else None
        if not items:
            raise MicobooksError(f"No quotation found for ISBN/EAN {identifier}.")

        item = self._select_item(items, identifier)
        try:
            return BookQuote(
                title=str(item["title"]),
                isbn=item.get("isbn_identifier"),
                ean=item.get("ean_identifier"),
                seller_profit=float(item["seller_profit"]),
                image_url=item.get("url_image"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise MicobooksError("Micobooks returned an unexpected quotation format.") from error

    @staticmethod
    def _normalize_identifier(value: str) -> str:
        identifier = value.replace("-", "").replace(" ", "")
        if not identifier or not ISBN_PATTERN.fullmatch(identifier):
            raise ValueError("ISBN/EAN must contain only digits, hyphens, spaces, or X.")
        if not 10 <= len(identifier) <= 13:
            raise ValueError("ISBN/EAN must contain between 10 and 13 characters.")
        return identifier.upper()

    @staticmethod
    def _select_item(items: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
        for item in items:
            identifiers = {
                str(item.get("isbn_identifier", "")),
                str(item.get("ean_identifier", "")),
            }
            if identifier in identifiers:
                return item
        return items[0]
