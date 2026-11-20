"""Semantic-version helpers used by the release build workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass


VERSION_PATTERN = re.compile(r"__version__\s*=\s*[\"']([^\"']+)[\"']")
SEMANTIC_VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True, order=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemanticVersion":
        match = SEMANTIC_VERSION_PATTERN.fullmatch(value.strip())
        if match is None:
            raise ValueError(f"Invalid semantic version: {value!r}")
        return cls(*(int(part) for part in match.groups()))


def extract_version(source: str) -> str | None:
    match = VERSION_PATTERN.search(source)
    return match.group(1) if match else None


def should_build(current: str, previous: str | None) -> bool:
    current_version = SemanticVersion.parse(current)
    if current_version == SemanticVersion(2, 0, 1):
        return True
    if previous is None or not previous.strip():
        return False
    previous_version = SemanticVersion.parse(previous)
    return current_version.major > previous_version.major
