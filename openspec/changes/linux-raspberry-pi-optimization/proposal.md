# Proposal: Optimize Linux deployment for Raspberry Pi 4

## Intent

Make the Micobooks scraper practical to run on a Raspberry Pi 4 running
Linux, with predictable memory and CPU usage while preserving the existing
FastAPI API, browser workflow, HTTPS launcher, and local history behavior.

## Current state

The project documents Windows-first virtual-environment and firewall setup.
Image processing doubles the input dimensions and runs several Tesseract
passes concurrently, which can create avoidable CPU and memory pressure on a
four-core Raspberry Pi. The dependency ranges are not accompanied by an
ARM/Linux installation or service workflow.

## Target state

The application SHALL support a documented Raspberry Pi 4 Linux setup,
provide ARM-compatible dependency guidance, and bound OCR resource usage
without changing the observable quote or history API behavior.

## Scope

- Document supported Raspberry Pi 4 Linux prerequisites and installation.
- Document native Tesseract and zxing/Pillow dependency requirements for ARM.
- Add a Linux-friendly HTTPS startup workflow and optional systemd guidance.
- Make OCR preprocessing and concurrency configurable or bounded for Pi-class
  hardware.
- Add focused tests for the changed configuration and resource limits.
- Preserve the existing Windows setup and default behavior where practical.

## Impact

- **API:** Existing endpoints and response shapes remain unchanged; image
  processing may take longer but should use bounded resources.
- **Frontend:** No functional changes are required.
- **Persistence:** Local JSON history remains unchanged.
- **Operations:** README and launcher guidance gain Raspberry Pi/Linux
  instructions, including certificate and LAN-only access requirements.

## Out of scope

- Replacing FastAPI, Uvicorn, Tesseract, Pillow, or zxingcpp.
- Supporting arbitrary ARM boards or 32-bit operating systems beyond the
  documented Raspberry Pi 4 target.
- Introducing a database, authentication, remote job queue, or cloud OCR.
- Disabling HTTPS or weakening the existing LAN-only access policy.
