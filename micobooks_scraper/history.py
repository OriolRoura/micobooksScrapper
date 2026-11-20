"""Local JSON storage for analyzed book records."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import threading
from typing import Any
from uuid import uuid4


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEPLOYMENT_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else _PROJECT_ROOT
DEFAULT_HISTORY_PATH = _DEPLOYMENT_ROOT / "data" / "analyzed_books.json"


def canonical_isbn(identifier: str) -> str:
    """Normalize an ISBN and map 978 ISBN-13 values to ISBN-10 when possible."""
    normalized = "".join(character for character in identifier.upper() if character.isdigit() or character == "X")
    if len(normalized) == 13 and normalized.startswith("978"):
        body = normalized[3:12]
        checksum = (11 - sum((10 - index) * int(digit) for index, digit in enumerate(body)) % 11) % 11
        return body + ("X" if checksum == 10 else str(checksum))
    return normalized


class HistoryStore:
    """Persist analyzed ISBN records in a small local JSON file."""

    def __init__(self, path: Path = DEFAULT_HISTORY_PATH) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def add(
        self,
        isbn: str,
        *,
        title: str | None = None,
        seller_profit: float | None = None,
        found: bool,
    ) -> dict[str, Any]:
        canonical_identifier = canonical_isbn(isbn)
        record = {
            "id": str(uuid4()),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "isbn": isbn,
            "title": title,
            "seller_profit": seller_profit,
            "found": found,
            "sell_decision": None,
        }
        with self._lock:
            records = self._read()
            existing = next(
                (item for item in records if canonical_isbn(str(item.get("isbn", ""))) == canonical_identifier),
                None,
            )
            if existing is not None:
                if found or not existing.get("found"):
                    existing["analyzed_at"] = record["analyzed_at"]
                    existing["isbn"] = isbn
                    existing["title"] = title if title is not None else existing.get("title")
                    existing["seller_profit"] = seller_profit if seller_profit is not None else existing.get("seller_profit")
                    existing["found"] = found or bool(existing.get("found"))
                self._write(records)
                return existing
            records.append(record)
            self._write(records)
        return record

    def all(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(reversed(self._read()))

    def set_sell_decision(self, record_id: str, decision: str) -> dict[str, Any]:
        with self._lock:
            records = self._read()
            for record in records:
                if record["id"] == record_id:
                    record["sell_decision"] = decision
                    self._write(records)
                    return record
        raise KeyError(record_id)

    def _read(self) -> list[dict[str, Any]]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def _write(self, records: list[dict[str, Any]]) -> None:
        temporary_path = self.path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_path.replace(self.path)
