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

## Test

```powershell
python -m unittest discover -s tests -v
```
