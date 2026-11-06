# Micobooks ISBN scraper

Small Python scraper for querying the Micobooks income calculator with an ISBN/EAN.

## Requirements

- Python 3.10 or newer
- Dependencies in `requirements.txt`

Install the backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run it

From the project directory:

```powershell
python -m micobooks_scraper
```

The default ISBN is `9788497593182`. To query another book, set `ISBN`:

```powershell
$env:ISBN = "9788497593182"
python -m micobooks_scraper
```

The client sends the same request as the calculator page and extracts `seller_profit` from the JSON response. Use a reasonable request rate and follow Micobooks' terms before automating larger batches.

## Run the backend

```powershell
python -m micobooks_scraper.api
```

The API listens on `http://127.0.0.1:8000`. Check it with `GET /health` or send an ISBN to `POST /api/quote`:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/quote -Method Post -ContentType "application/json" -Body '{"isbn":"9788497593182"}'
```

Set `ALLOWED_ORIGINS` to a comma-separated list when the webpage is served from another origin.

Open the mobile-first webpage at `http://127.0.0.1:8000/app/`. It supports camera/image capture and manual ISBN lookup. The image endpoint runs server-side OCR using Tesseract. On Debian/Ubuntu Linux, install the executable with `sudo apt install tesseract-ocr`.

## Analysis history

Each ISBN analysis is stored locally in `data/analyzed_books.json`. The file is runtime data and is ignored by Git. Records have this shape:

```json
{
	"id": "record-identifier",
	"analyzed_at": "2026-11-03T12:00:00+00:00",
	"isbn": "9788497593182",
	"title": "Book title or null",
	"seller_profit": 0.28,
	"found": true,
	"sell_decision": null
}
```

The history API is ready for the future history view:

- `GET /api/history` returns newest records first.
- `PATCH /api/history/{id}/decision` accepts `{"decision":"sell"}` or `{"decision":"not_sell"}`.

## Test

```powershell
python -m unittest discover -s tests -v
```
