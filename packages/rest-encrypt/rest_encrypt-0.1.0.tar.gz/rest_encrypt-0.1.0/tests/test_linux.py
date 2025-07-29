import pytest
from rest_encrypt.platforms.linux import ScryptWrapper, HEADER


def test_scrypt_roundtrip(tmp_path):
    pw_file = tmp_path / "pw"
    pw_file.write_text("pass")
    wrapper = ScryptWrapper(passphrase_path=str(pw_file))
    data = b"secret"
    blob = wrapper.protect(data)
    assert blob.startswith(HEADER)
    out = wrapper.unprotect(blob)
    assert out == data


def test_scrypt_bad_header(tmp_path):
    pw_file = tmp_path / "pw"
    pw_file.write_text("pass")
    wrapper = ScryptWrapper(passphrase_path=str(pw_file))
    with pytest.raises(ValueError):
        wrapper.unprotect(b"BAD" + b"something")

