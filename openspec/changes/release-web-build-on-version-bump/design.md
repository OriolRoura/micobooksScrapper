# Design: Release-triggered server executable

## Version source

Introduce a single machine-readable semantic version in a repository file
that is suitable for both Python and GitHub Actions. The application version
reported by FastAPI and the workflow version must come from this same source;
duplicated version literals are not allowed.

The workflow must validate that the version is a valid `MAJOR.MINOR.PATCH`
value before comparing it. Invalid versions must fail the workflow rather
than silently skipping the build.

## Workflow trigger and comparison

Add a GitHub Actions workflow triggered by pushes to the repository. It must
read the current version and determine the previous version from the prior
release tag or the previous version-bearing revision. The comparison must
handle the first release explicitly.

The build condition is:

```text
current.major > previous.major
OR
(current.major == previous.major AND current.minor > previous.minor)
```

The workflow should expose the decision in its logs and complete successfully
without producing a release artifact when the condition is false.

## Executable contents

Use an application bundler such as PyInstaller to create a platform-specific
one-file executable. The bundle must include the Python runtime, FastAPI
application, Uvicorn launcher, Python dependencies, and the complete
`frontend/` directory.

The executable entry point must start the existing HTTPS server and preserve
the current host, port, certificate, private-key, LAN-only access, and
`/app/` behavior. It must not require Python to be installed on the target
server.

Build separate artifacts for each supported target, such as Windows x64 and
Linux ARM64. A binary built for one operating system or architecture must not
be presented as compatible with another.

## External runtime requirements

Certificates and private keys must remain external files. Embedding a private
key in an executable would not provide meaningful secrecy and would prevent
normal certificate rotation.

Native Tesseract must either be bundled through a supported platform-specific
runtime layout or be installed separately and located explicitly at startup.
The build must fail clearly when OCR dependencies are unavailable.

Writable history and other runtime data must be stored outside the executable
in a documented data directory. The executable must not attempt to write
inside its temporary extraction directory.

## Artifact publishing

Build versioned executable artifacts. Each artifact must include the target
platform and architecture in its name, for example
`micobooks-server-2.0.1-windows-x64.exe` or
`micobooks-server-2.0.1-linux-arm64`.

Upload the executables as GitHub Actions artifacts. After all target builds
complete, create the `v<version>` tag at the triggering commit and create the
matching GitHub Release with all executables attached as release assets. If
the release already exists, replace its assets rather than creating a second
release. Generated executables must not be committed to the repository.

## Compatibility

The existing `/app/` deployment path and frontend asset paths must remain
valid. The build process must not rewrite URLs or alter source files.
