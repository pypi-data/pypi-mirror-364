"""Pass-through serializer for Python dicts."""

from __future__ import annotations

import ast


class DictSerializer:
    def loads(self, text: str) -> dict:
        """Evaluate ``text`` as a Python literal."""
        return ast.literal_eval(text)

    def dumps(self, data: dict) -> str:
        """Return ``repr(data)``."""
        return repr(data)
