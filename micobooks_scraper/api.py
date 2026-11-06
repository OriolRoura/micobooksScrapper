"""HTTP API for the Micobooks scraper."""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Literal

from fastapi import File, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .client import MicobooksClient, MicobooksError
from .history import HistoryStore
from .ocr import OcrError, extract_isbn_candidates


logger = logging.getLogger(__name__)


class QuoteRequest(BaseModel):
    isbn: str = Field(min_length=10, max_length=17)


class QuoteResponse(BaseModel):
    title: str
    isbn: str | None
    ean: str | None
    seller_profit: float
    image_url: str | None


class SellDecisionRequest(BaseModel):
    decision: Literal["sell", "not_sell"]


MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _allowed_origins() -> list[str]:
    configured_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


app = FastAPI(title="Micobooks Scraper API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
history_store = HistoryStore()


@app.get("/")
def index() -> dict[str, str]:
    return {
        "name": "Micobooks Scraper API",
        "health": "/health",
        "docs": "/docs",
        "frontend": "/app/",
        "quote_endpoint": "POST /api/quote",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/quote", response_model=QuoteResponse)
def quote(request: QuoteRequest) -> QuoteResponse:
    try:
        result = MicobooksClient().get_quote(request.isbn)
    except ValueError as error:
        history_store.add(request.isbn, found=False)
        raise HTTPException(status_code=422, detail=str(error)) from error
    except MicobooksError as error:
        history_store.add(request.isbn, found=False)
        raise HTTPException(status_code=502, detail=str(error)) from error

    history_store.add(
        result.isbn or request.isbn,
        title=result.title,
        seller_profit=result.seller_profit,
        found=True,
    )
    return QuoteResponse(
        title=result.title,
        isbn=result.isbn,
        ean=result.ean,
        seller_profit=result.seller_profit,
        image_url=result.image_url,
    )


@app.post("/api/quote-from-image", response_model=QuoteResponse)
async def quote_from_image(image: UploadFile = File(...)) -> QuoteResponse:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload an image file.")

    image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")

    try:
        candidates = extract_isbn_candidates(image_bytes)
    except OcrError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    if not candidates:
        raise HTTPException(status_code=422, detail="No valid ISBN was detected in the image.")

    for candidate in candidates:
        try:
            logger.info("ISBN detected: %s. Starting Micobooks search.", candidate)
            result = MicobooksClient().get_quote(candidate)
            history_store.add(
                result.isbn or candidate,
                title=result.title,
                seller_profit=result.seller_profit,
                found=True,
            )
            return QuoteResponse(
                title=result.title,
                isbn=result.isbn,
                ean=result.ean,
                seller_profit=result.seller_profit,
                image_url=result.image_url,
            )
        except MicobooksError:
            history_store.add(candidate, found=False)
            continue

    searched_identifiers = ", ".join(candidates)
    raise HTTPException(
        status_code=404,
        detail=f"No price found for ISBN/EAN: {searched_identifiers}.",
    )


@app.get("/api/history")
def get_history() -> list[dict[str, object]]:
    return history_store.all()


@app.patch("/api/history/{record_id}/decision")
def set_sell_decision(record_id: str, request: SellDecisionRequest) -> dict[str, object]:
    try:
        return history_store.set_sell_decision(record_id, request.decision)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="History record not found.") from error


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("micobooks_scraper.api:app", host="127.0.0.1", port=8000, reload=True)
