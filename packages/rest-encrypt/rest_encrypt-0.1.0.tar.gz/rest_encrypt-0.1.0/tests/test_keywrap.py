import platform
from rest_encrypt.keywrap import get_wrapper
from rest_encrypt.platforms.linux import ScryptWrapper


def test_get_wrapper_linux(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    wrapper = get_wrapper()
    assert isinstance(wrapper, ScryptWrapper)

