# Proposal: Build a deployable server executable on release version bumps

## Intent

Create a repeatable, platform-specific executable containing the Micobooks
backend and frontend so an operator can copy one executable to a server,
run it, and access the deployed web application over HTTPS.

## Current state

The repository contains a FastAPI backend and frontend files in `frontend/`,
but it has no canonical project version, release-triggered build workflow, or
executable deployment artifact.

## Target state

The project SHALL define one canonical semantic version and SHALL create a
platform-specific executable containing the backend, frontend, Python
runtime, and Python dependencies when a pushed version increases the major or
minor component compared with the previous release version (for example,
`2.0.0` to `2.1.0` or `2.0.0` to `3.0.0`). Patch-only increases are excluded.

Running the executable SHALL start the HTTPS server and serve the frontend at
the existing `/app/` path without requiring a Python installation.

## Scope

- Add a canonical semantic version that can be read by the application and
  the build workflow.
- Add a GitHub Actions workflow triggered by pushes to the repository.
- Compare the pushed version with the previous release version using
  semantic-version rules.
- Build and publish a versioned executable containing the FastAPI server,
  frontend, Python runtime, and Python dependencies when a major or minor
  version increase is detected.
- Produce separate executables for each supported target platform rather than
  claiming that one binary runs on Windows and Linux.
- Upload the executables as workflow artifacts and automatically create the
  matching `v<version>` tag and GitHub Release, including all executables as
  release assets.
- Keep private keys and mutable runtime data outside the executable.
- Document native Tesseract as an included or separately installed runtime
  dependency for each target platform.

## Impact

- **API:** The existing API and its response shapes remain unchanged. The
  executable starts the same HTTPS application.
- **Frontend:** The existing `frontend/` files are bundled into the
  executable and remain available at `/app/`.
- **Persistence:** No persistence behavior changes.
- **Operations:** Maintainers gain downloadable, platform-specific
  executables. Operators can run the executable on a matching server without
  installing Python.

## Out of scope

- Automatically deploying the executable to a hosting provider.
- Producing one universal binary for all operating systems and CPU
  architectures.
- Publishing artifacts for patch-only version changes or version downgrades.
- Committing generated executables to the repository.
