"""Serializer for ``.env`` style ``KEY=VALUE`` pairs."""

from __future__ import annotations

"""Serializer for ``.env`` style key-value files."""

from io import StringIO
from typing import Dict

from dotenv import dotenv_values


class ENVSerializer:
    def loads(self, text: str) -> dict:
        """Parse ``text`` containing ``KEY=VALUE`` pairs."""

        values = dotenv_values(stream=StringIO(text))
        return {k: v for k, v in values.items() if v is not None}

    def dumps(self, data: Dict[str, str]) -> str:
        """Serialise ``data`` to ``KEY=VALUE`` lines."""

        return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"
