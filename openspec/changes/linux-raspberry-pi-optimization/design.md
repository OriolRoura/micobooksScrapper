# Design: Raspberry Pi 4 Linux optimization

## Runtime configuration

Add a small, typed configuration surface for OCR resource limits. Defaults
must preserve the current Windows behavior unless a Linux/Pi deployment opts
into the Pi profile. Invalid values must fail explicitly at startup or request
handling rather than silently falling back.

The configuration should cover:

- maximum OCR worker count;
- maximum image dimensions or preprocessing scale;
- an optional profile or environment variables suitable for constrained
  Raspberry Pi hardware.

The implementation must avoid unbounded work per upload and must not create
more concurrent Tesseract processes than the configured limit.

## Dependency and platform support

Keep the existing dependency ranges unless an ARM/Linux compatibility issue
requires a narrow, documented adjustment. Document 64-bit Raspberry Pi OS
as the supported baseline, with Python, native Tesseract, and required build
or binary packages installed through the OS package manager where
appropriate.

## Launcher and service workflow

Keep `micobooks_scraper.server` as the canonical launcher. Add Linux examples
for virtual-environment setup, certificate paths, LAN binding, health checks,
and an optional systemd unit template or guidance. The service workflow must
retain HTTPS and the default LAN-only request filter.

## Validation

Tests should verify configuration parsing, worker/scale bounds, and that
existing ISBN extraction and API behavior remain intact. Documentation should
include a repeatable Raspberry Pi smoke test using `/health` and an image
quote request.
