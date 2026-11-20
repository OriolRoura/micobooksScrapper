# Tasks

## 1. Raspberry Pi runtime configuration

- [x] 1.1 Add typed OCR configuration with explicit defaults and validation
- [x] 1.2 Bound image preprocessing dimensions for the Pi profile
- [x] 1.3 Bound Tesseract worker concurrency for the Pi profile
- [x] 1.4 Add focused unittest coverage for valid and invalid configuration

## 2. Linux packaging and launcher

- [ ] 2.1 Verify dependency installation on supported 64-bit Raspberry Pi OS
- [x] 2.2 Preserve Windows dependency and launcher behavior
- [x] 2.3 Add Linux-friendly certificate, host, port, and health-check guidance
- [x] 2.4 Document optional systemd operation without committing secrets or
  runtime data

## 3. Documentation and compatibility

- [x] 3.1 Document native Tesseract and ARM/Linux prerequisites
- [x] 3.2 Document the Pi resource profile and tuning trade-offs
- [x] 3.3 Confirm LAN-only access and HTTPS requirements remain explicit
- [x] 3.4 Document Raspberry Pi smoke-test steps

## 4. Verification

- [x] 4.1 Run focused OCR, configuration, and launcher tests
- [x] 4.2 Run the complete unittest suite
- [ ] 4.3 Validate the documented Linux setup on a Raspberry Pi 4 or
  equivalent ARM64 environment
