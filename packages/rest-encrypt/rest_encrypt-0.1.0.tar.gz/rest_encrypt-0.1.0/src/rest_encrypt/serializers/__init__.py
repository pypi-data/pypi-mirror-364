# src/rest_encrypt/serializers/__init__.py
"""Collection of supported serializers."""

from .json_serializer import JSONSerializer
from .toml_serializer import TOMLSerializer
from .ini_serializer import INISerializer
from .env_serializer import ENVSerializer
from .dict_serializer import DictSerializer

SERIALIZERS = {
    "json": JSONSerializer(),
    "toml": TOMLSerializer(),
    "ini": INISerializer(),
    "env": ENVSerializer(),
    "dict": DictSerializer(),
}


def get(serializer_name: str):
    """Return the serializer instance matching ``serializer_name``."""

    try:
        return SERIALIZERS[serializer_name.lower()]
    except KeyError:
        raise ValueError(f"Unknown serializer '{serializer_name}'.")
