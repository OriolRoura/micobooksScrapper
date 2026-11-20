# Tasks

## 1. Version and workflow foundation

- [x] 1.1 Add one canonical semantic version source and make the FastAPI
  application read it.
- [x] 1.2 Add a GitHub Actions workflow that runs on repository pushes.
- [x] 1.3 Validate the current version and obtain the previous release version
  before deciding whether to build.
- [x] 1.4 Implement major- and minor-version-increase conditions,
  including first-release behavior and explicit workflow logging.

## 2. Deployable server executable

- [x] 2.1 Add an executable entry point that starts the existing HTTPS server
  and serves the bundled frontend at `/app/`.
- [x] 2.2 Configure a one-file bundler to include the Python runtime,
  backend, dependencies, and frontend assets.
- [x] 2.3 Build separate executable artifacts for each supported operating
  system and architecture.
- [x] 2.4 Verify executable startup without a Python installation and verify
  that certificate, Tesseract, and writable-data requirements fail clearly
  when missing.
- [x] 2.5 Keep certificates, private keys, runtime data, virtual
  environments, and repository metadata out of the executable.
- [x] 2.6 Upload executables as workflow artifacts and automatically create
  the matching tag and GitHub Release with those executables as assets.
- [x] 2.7 Preserve the existing `/app/` URL and frontend asset references.

## 3. Verification

- [x] 3.1 Add focused tests for valid, invalid, major-bump, patch-bump,
  minor-bump, downgrade, and first-release version decisions.
- [x] 3.2 Add a packaging check for bundled frontend assets and excluded
  sensitive/runtime files.
- [ ] 3.3 Add a smoke test that runs each target executable and checks the
  HTTPS health endpoint and `/app/` page.
- [x] 3.4 Validate the workflow syntax and run the focused test suite.
