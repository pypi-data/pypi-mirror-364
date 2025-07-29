import pytest
from rest_encrypt.serializers import get

DATA = {"a": 1, "b": "two", "section": {"x": "y"}}


def _roundtrip(name: str):
    ser = get(name)
    dumped = ser.dumps(DATA)
    loaded = ser.loads(dumped)
    assert isinstance(loaded, dict)
    assert str(loaded.get("a")) == "1"


def test_json_roundtrip():
    _roundtrip("json")


def test_toml_roundtrip():
    _roundtrip("toml")


def test_ini_roundtrip():
    _roundtrip("ini")


def test_env_roundtrip():
    ser = get("env")
    dumped = ser.dumps({"KEY": "VAL"})
    assert ser.loads(dumped)["KEY"] == "VAL"


def test_dict_roundtrip():
    _roundtrip("dict")


def test_unknown_serializer():
    with pytest.raises(ValueError):
        get("unknown")
