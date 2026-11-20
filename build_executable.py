"""Build a one-file server executable with PyInstaller."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

import PyInstaller.__main__


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Micobooks server executable.")
    parser.add_argument("--name", required=True, help="Output executable name without a platform suffix.")
    options = parser.parse_args()

    dist_directory = PROJECT_ROOT / "dist"
    build_directory = PROJECT_ROOT / "build"
    shutil.rmtree(dist_directory, ignore_errors=True)
    shutil.rmtree(build_directory, ignore_errors=True)

    PyInstaller.__main__.run(
        [
            str(PROJECT_ROOT / "run_server.py"),
            "--name",
            options.name,
            "--onefile",
            "--clean",
            "--noconfirm",
            "--paths",
            str(PROJECT_ROOT),
            "--distpath",
            str(dist_directory),
            "--workpath",
            str(build_directory),
            "--specpath",
            str(build_directory),
            "--add-data",
            f"{PROJECT_ROOT / 'frontend'}{';' if sys.platform == 'win32' else ':'}frontend",
        ]
    )


if __name__ == "__main__":
    main()
