"""ISBN extraction from uploaded book images."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import re

from PIL import Image, ImageOps
import pytesseract
import zxingcpp


def _configure_tesseract() -> None:
    """Use the standard Windows installation path when PATH is stale."""
    windows_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if windows_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(windows_path)


_configure_tesseract()


class OcrError(RuntimeError):
    """Raised when OCR cannot be completed."""


def extract_isbn_candidates(image_bytes: bytes) -> list[str]:
    """Read barcodes first, then use OCR for printed ISBN fallback."""
    try:
        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert("L")
        image = ImageOps.autocontrast(image)
        image = image.resize((image.width * 2, image.height * 2))
        candidates = extract_barcode_candidates(image)
        label_area = image.crop((0, image.height // 2, image.width, image.height))
        thresholded_label = label_area.point(lambda value: 255 if value > 150 else 0)
        ocr_passes = [
            (label_area, 7),
            (label_area, 11),
            (thresholded_label, 7),
            (thresholded_label, 11),
            (image, 11),
        ]
        with ThreadPoolExecutor(max_workers=min(4, len(ocr_passes))) as executor:
            text_parts = list(executor.map(_run_ocr, ocr_passes))
        text = "\n".join(text_parts)
    except pytesseract.TesseractNotFoundError as error:
        raise OcrError("Tesseract is not installed or is not available on PATH.") from error
    except (OSError, ValueError) as error:
        raise OcrError("The uploaded image could not be processed.") from error

    candidates = list(candidates)
    normalized_text = text.replace("ISBN", " ").replace("isbn", " ")
    for line in normalized_text.splitlines():
        # OCR often reads digits as letters and inserts spaces between groups.
        corrected_line = line.translate(str.maketrans({"O": "0", "o": "0", "Q": "0", "I": "1", "l": "1", "|": "1"}))
        compact_line = re.sub(r"[^0-9Xx]", "", corrected_line).upper()
        possible_identifiers = re.findall(r"[0-9Xx]{10,13}", compact_line)
        if 10 <= len(compact_line) <= 13:
            possible_identifiers.append(compact_line)
        for identifier in possible_identifiers:
            if identifier not in candidates and _is_valid_isbn(identifier):
                candidates.append(identifier)
    return candidates


def _run_ocr(ocr_pass: tuple[Image.Image, int]) -> str:
    image, page_mode = ocr_pass
    return pytesseract.image_to_string(image, config=f"--psm {page_mode}")


def extract_barcode_candidates(image: Image.Image) -> list[str]:
    """Decode EAN/ISBN barcodes from a Pillow image."""
    candidates: list[str] = []
    try:
        barcodes = zxingcpp.read_barcodes(image)
    except (TypeError, ValueError):
        return candidates

    for barcode in barcodes:
        identifier = re.sub(r"[^0-9Xx]", "", barcode.text).upper()
        if identifier not in candidates and _is_valid_isbn(identifier):
            candidates.append(identifier)
    return candidates


def _is_valid_isbn(identifier: str) -> bool:
    if len(identifier) == 10:
        if not re.fullmatch(r"[0-9]{9}[0-9X]", identifier):
            return False
        return sum((10 - index) * (10 if digit == "X" else int(digit)) for index, digit in enumerate(identifier)) % 11 == 0

    if len(identifier) == 13 and identifier.isdigit():
        checksum = sum((1 if index % 2 == 0 else 3) * int(digit) for index, digit in enumerate(identifier[:12]))
        return (10 - checksum % 10) % 10 == int(identifier[-1])

    return False
