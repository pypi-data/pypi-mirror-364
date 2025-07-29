# src/rest_encrypt/serializers/json_serializer.py
"""JSON serializer using :mod:`json`."""

import json


class JSONSerializer:
    def loads(self, text: str) -> dict:
        """Parse a JSON string into a dictionary."""
        return json.loads(text)

    def dumps(self, data: dict) -> str:
        """Serialise ``data`` as formatted JSON."""
        return json.dumps(data, indent=2, sort_keys=True)
