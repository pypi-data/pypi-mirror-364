import platform

import pytest


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
def test_dpapi_roundtrip():
    from rest_encrypt.platforms.windows import DPAPIWrapper, DPAPIScope

    wrapper = DPAPIWrapper(scope=DPAPIScope.USER)
    data = b"secret"
    blob = wrapper.protect(data)
    assert wrapper.unprotect(blob) == data
