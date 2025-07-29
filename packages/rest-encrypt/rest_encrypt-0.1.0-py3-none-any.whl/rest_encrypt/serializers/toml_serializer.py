"""TOML serializer using :mod:`tomllib` (or ``tomli`` on <3.11)."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    import tomllib as toml
else:  # pragma: no cover - fallback for old Python
    import tomli as toml

import tomli_w


class TOMLSerializer:
    def loads(self, text: str) -> dict:
        """Parse TOML formatted ``text``."""
        return toml.loads(text)

    def dumps(self, data: dict) -> str:
        """Serialise ``data`` to TOML."""
        return tomli_w.dumps(data)
