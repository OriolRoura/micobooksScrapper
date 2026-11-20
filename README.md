# Micobooks ISBN scraper

Personal-use web tool that captures or uploads a book image, detects an ISBN locally on the server, queries Micobooks, and displays the seller estimate.

## Requirements

- Python 3.10 or newer
- Native Tesseract OCR executable
- HTTPS certificate files for the web launcher:
	- `certs/server.crt`
	- `certs/server.key`

Python dependencies are pinned by compatible version ranges in `requirements.txt`.

Release builds can also produce a platform-specific server executable. It
includes the Python runtime, API, dependencies, and frontend, so Python does
not need to be installed on the target server. Certificates remain external
files and native Tesseract must be installed or provided according to the
target platform's release instructions.

## Setup

Create the virtual environment if it does not exist:

```powershell
python -m venv .venv
```

Install all Python dependencies into it:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The Python package `pytesseract` is only a wrapper. Install native Tesseract separately:

```powershell
winget install UB-Mannheim.TesseractOCR
```

On Debian/Ubuntu Linux:

```bash
sudo apt install tesseract-ocr
```

### Raspberry Pi 4 Linux

The supported baseline is 64-bit Raspberry Pi OS on a Raspberry Pi 4. Install
the native prerequisites and create the project environment:

```bash
sudo apt update
sudo apt install python3-venv tesseract-ocr libzbar0
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Enable the bounded OCR profile for Pi-class CPU and memory resources:

```bash
export MICOBOOKS_OCR_PROFILE=raspberry-pi
.venv/bin/python -m micobooks_scraper.server \
  --host 0.0.0.0 --port 8443 \
  --cert certs/server.crt --key certs/server.key
```

The Pi profile uses one OCR worker, avoids the default image upscaling, and
limits the processed image dimension to 2048 pixels. Tune it with
`MICOBOOKS_OCR_MAX_WORKERS`, `MICOBOOKS_OCR_SCALE`, and
`MICOBOOKS_OCR_MAX_DIMENSION`; invalid values are reported explicitly.

For unattended operation, create a systemd unit such as
`/etc/systemd/system/micobooks.service` and adjust the user and project path:

```ini
[Unit]
Description=Micobooks scraper
After=network-online.target

[Service]
User=micobooks
WorkingDirectory=/opt/micobooksScrapper
Environment=MICOBOOKS_OCR_PROFILE=raspberry-pi
ExecStart=/opt/micobooksScrapper/.venv/bin/python -m micobooks_scraper.server
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable it with `sudo systemctl enable --now micobooks`. Keep the certificate
and private key readable only by the service account, and retain the default
LAN-only access policy.

Smoke-test the service from the Pi:

```bash
curl -k https://127.0.0.1:8443/health
curl -k -F "image=@sample-book.jpg" https://127.0.0.1:8443/api/quote-from-image
```

## Start the HTTPS server

From the project directory:

```powershell
.venv\Scripts\python.exe -m micobooks_scraper.server
```

The launcher binds to `0.0.0.0` and serves HTTPS on port `8443` using `certs/server.crt` and `certs/server.key`. By default, requests are accepted only from the same computer or private LAN addresses. `0.0.0.0` is only the bind address; do not put it in a browser URL.

On the same computer:

```text
https://127.0.0.1:8443/app/
```

From another device on the same LAN, replace the IP with the server's LAN address:

```text
https://192.168.2.46:8443/app/
```

Health check:

```text
https://192.168.2.46:8443/health
```

To customize the server:

```powershell
.venv\Scripts\python.exe -m micobooks_scraper.server --host 0.0.0.0 --port 9443 --cert certs\server.crt --key certs\server.key
```

Public-client filtering can be disabled only explicitly:

```powershell
.venv\Scripts\python.exe -m micobooks_scraper.server --allow-public-access
```

Do not use this option for normal operation. HTTPS encrypts traffic but does
not restrict who can connect. Do not configure router port forwarding or UPnP
for this personal-use service.

The certificate must cover the IP or hostname used in the browser. The mobile device must trust the local CA that signed the certificate. Never share `server.key` or `rootCA-key.pem`.

Allow the HTTPS port through Windows Firewall when testing from another device:

```powershell
New-NetFirewallRule -DisplayName "Micobooks HTTPS development" -Direction Inbound -Protocol TCP -LocalPort 8443 -Action Allow -Profile Private
```

Keep the firewall rule on the `Private` profile so the service is not opened
on public networks.

## Executable release builds

For versions that meet the release-build rule (an increase in the major or
minor component), push the version change to the repository's default branch.
Patch-only changes do not create a release. GitHub Actions then creates the matching Git tag and GitHub Release
automatically, with platform-specific server executables attached. The
executable includes the Python runtime, backend, dependencies, and frontend,
so Python is not required on the target server.

Copy the executable for the target operating system and architecture to the
server, together with:

- `certs/server.crt`
- `certs/server.key`
- a native Tesseract installation

Run the executable from its deployment directory:

```powershell
.\micobooks-server-2.0.1-windows-x64.exe
```

or on Linux:

```bash
./micobooks-server-2.0.1-linux-arm64
```

The default URL remains `https://<server-address>:8443/app/`. Runtime
history is stored in a `data/` directory beside the executable. Keep the
private key outside the executable and restrict its permissions.

## Features

- Mobile-first camera and image-upload flow.
- Server-side EAN/ISBN barcode decoding and Tesseract OCR fallback.
- Manual ISBN lookup.
- Local JSON history in `data/analyzed_books.json`.
- Automatic deduplication of ISBN-10 and equivalent `978` ISBN-13 values.
- History drawer with sell/not-sell decisions, JSON import, JSON download, and seller-profit totals.

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

The history API is used by the history drawer:

- `GET /api/history` returns newest records first.
- `PATCH /api/history/{id}/decision` accepts `{"decision":"sell"}` or `{"decision":"not_sell"}`.

## Test

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## OpenSpec

OpenSpec project configuration and the current behavior specifications live in
the [`openspec/`](openspec/) directory. Create proposed work under
`openspec/changes/<change-name>/` with the standard `proposal.md`,
`specs/`, `design.md`, and `tasks.md` artifacts. Completed changes move to
`openspec/changes/archive/`.

### Initialize OpenSpec workflows

The project files above are already prepared. The OpenSpec CLI still needs to
install the workflow skills that your AI assistant loads. In PowerShell, from
the repository root, run:

```powershell
irm https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/scripts/binary/install.ps1 | iex
openspec init --tools github-copilot
```

Restart VS Code after initialization. OpenSpec is used in the AI chat, not as a
separate server or interactive application:

```text
/openspec-explore
/openspec-propose add-a-short-change-name
/openspec-apply-change
/openspec-sync-specs
/openspec-archive-change
```

Review the generated proposal and tasks before applying them. Use
`openspec list`, `openspec show <change-name>`, and
`openspec validate <change-name>` in the terminal to inspect or validate
changes. If the addon exposes a different command spelling, use the exact
skill names created under `.agents/skills/`.
