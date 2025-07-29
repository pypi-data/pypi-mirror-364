"""INI file serializer using :mod:`configparser`."""

from __future__ import annotations

import configparser
from io import StringIO


class INISerializer:
    def loads(self, text: str) -> dict:
        """Parse ``text`` as an INI document."""
        parser = configparser.ConfigParser()
        parser.read_string(text)
        result: dict[str, dict[str, str]] = {}
        for section in parser.sections():
            result[section] = dict(parser.items(section))
        if parser.defaults():
            result.update(parser.defaults())
        return result

    def dumps(self, data: dict) -> str:
        """Serialise ``data`` to INI format."""
        parser = configparser.ConfigParser()
        for key, value in data.items():
            if isinstance(value, dict):
                parser[key] = {k: str(v) for k, v in value.items()}
            else:
                parser["DEFAULT"][key] = str(value)
        buf = StringIO()
        parser.write(buf)
        return buf.getvalue()
