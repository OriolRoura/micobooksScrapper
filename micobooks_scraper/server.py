"""Start the Micobooks API with the project's external HTTPS configuration."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import uvicorn

from .api import app
from .ocr import validate_tesseract

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEPLOYMENT_ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else PROJECT_ROOT
DEFAULT_CERTIFICATE = DEPLOYMENT_ROOT / "certs" / "server.crt"
DEFAULT_KEY = DEPLOYMENT_ROOT / "certs" / "server.key"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start the Micobooks HTTPS server.")
    parser.add_argument("--host", default="0.0.0.0", help="Interface to bind to (default: all interfaces).")
    parser.add_argument("--port", type=int, default=8443, help="HTTPS port (default: 8443).")
    parser.add_argument("--cert", type=Path, default=DEFAULT_CERTIFICATE, help="TLS certificate path.")
    parser.add_argument("--key", type=Path, default=DEFAULT_KEY, help="TLS private key path.")
    parser.add_argument(
        "--allow-public-access",
        action="store_true",
        help="Disable LAN-only filtering (use only for intentional public exposure).",
    )
    return parser


def main() -> None:
    options = build_parser().parse_args()
    certificate = options.cert.resolve()
    private_key = options.key.resolve()

    missing = [str(path) for path in (certificate, private_key) if not path.is_file()]
    if missing:
        missing_paths = ", ".join(missing)
        raise SystemExit(f"Cannot start HTTPS server. Missing TLS file(s): {missing_paths}")

    try:
        validate_tesseract()
    except RuntimeError as error:
        raise SystemExit(f"Cannot start HTTPS server. {error}") from error

    if options.allow_public_access:
        import os

        os.environ["ALLOW_PUBLIC_ACCESS"] = "1"

    print(f"Starting HTTPS server at https://{options.host}:{options.port}")
    print("Use the machine's LAN IP in the browser, not 0.0.0.0.")
    print(
        "Access policy: public clients allowed."
        if options.allow_public_access
        else "Access policy: localhost and private-LAN clients only."
    )
    uvicorn.run(
        app,
        host=options.host,
        port=options.port,
        ssl_certfile=str(certificate),
        ssl_keyfile=str(private_key),
    )


if __name__ == "__main__":
    main()
