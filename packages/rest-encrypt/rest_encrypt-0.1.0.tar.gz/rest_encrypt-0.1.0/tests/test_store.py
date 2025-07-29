from pathlib import Path

import pytest

from rest_encrypt.store import SecretStore


@pytest.fixture()
def tmp_store(tmp_path: Path):
    secrets = tmp_path / "secrets.enc"
    wrapped = tmp_path / "wrapped.key"
    passphrase = tmp_path / "passphrase"
    passphrase.write_text("testpass")
    store = SecretStore(
        secrets_path=secrets,
        wrapped_key_path=wrapped,
        scope="user",
        passphrase_path=str(passphrase),
    )
    return store


def test_roundtrip_and_rotate(tmp_store: SecretStore):
    data = {"foo": "bar"}
    tmp_store.init_from_plain(data)
    loaded = tmp_store.load()
    assert loaded == data

    tmp_store.rotate_data_key()
    loaded2 = tmp_store.load()
    assert loaded2 == data


def test_inject_env_process(tmp_store: SecretStore, monkeypatch):
    env = {}
    monkeypatch.setattr("os.environ", env, raising=False)
    tmp_store.inject_env({"FOO": "BAR"}, scope="process")
    assert env["FOO"] == "BAR"


def test_inject_env_invalid_scope(tmp_store: SecretStore):
    with pytest.raises(ValueError):
        tmp_store.inject_env({}, scope="invalid")

