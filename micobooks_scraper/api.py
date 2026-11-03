"""HTTP API for the Micobooks scraper."""

from __future__ import annotations

import os
import logging
from pathlib import Path

from fastapi import File, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .client import MicobooksClient, MicobooksError
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
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


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
        raise HTTPException(status_code=422, detail=str(error)) from error
    except MicobooksError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

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
            return QuoteResponse(
                title=result.title,
                isbn=result.isbn,
                ean=result.ean,
                seller_profit=result.seller_profit,
                image_url=result.image_url,
            )
        except MicobooksError:
            continue

    raise HTTPException(status_code=404, detail="No detected ISBN was found by Micobooks.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("micobooks_scraper.api:app", host="127.0.0.1", port=8000, reload=True)
