# src/rest_encrypt/platforms/windows.py
"""Windows DPAPI based key wrapper."""

import ctypes
import ctypes.wintypes as wt
from enum import Enum

CRYPTPROTECT_LOCAL_MACHINE = 0x4


class DPAPIScope(str, Enum):
    """Scope for DPAPI operations."""

    USER = "user"
    MACHINE = "machine"


class DPAPIWrapper:
    """Wrap and unwrap keys using Windows DPAPI."""

    def __init__(self, scope: str = DPAPIScope.USER) -> None:
        self.scope = scope

    def protect(self, data: bytes) -> bytes:
        """Encrypt ``data`` using DPAPI."""
        flags = CRYPTPROTECT_LOCAL_MACHINE if self.scope == "machine" else 0
        return _crypt_protect(data, flags)

    def unprotect(self, blob: bytes) -> bytes:
        """Decrypt ``blob`` previously returned by :meth:`protect`."""
        flags = CRYPTPROTECT_LOCAL_MACHINE if self.scope == "machine" else 0
        return _crypt_unprotect(blob, flags)


# DATA_BLOB struct
class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wt.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _bytes_to_blob(data: bytes) -> DATA_BLOB:
    """Convert ``data`` to a ``DATA_BLOB`` structure."""
    buf = ctypes.create_string_buffer(data)
    return DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))


def _blob_to_bytes(blob: DATA_BLOB) -> bytes:
    """Extract bytes from a ``DATA_BLOB`` returned by DPAPI."""
    size = int(blob.cbData)
    addr = ctypes.addressof(blob.pbData.contents)
    return ctypes.string_at(addr, size)


def _crypt_protect(data: bytes, flags: int = 0) -> bytes:
    """Call ``CryptProtectData`` via ``ctypes``."""
    CryptProtectData = ctypes.windll.crypt32.CryptProtectData
    CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        wt.LPCWSTR,
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wt.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    CryptProtectData.restype = wt.BOOL

    in_blob = _bytes_to_blob(data)
    out_blob = DATA_BLOB()

    if not CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        flags,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()

    result = _blob_to_bytes(out_blob)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return result


def _crypt_unprotect(blob: bytes, flags: int = 0) -> bytes:
    """Call ``CryptUnprotectData`` via ``ctypes``."""
    CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
    CryptUnprotectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        ctypes.POINTER(wt.LPWSTR),
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wt.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    CryptUnprotectData.restype = wt.BOOL

    in_blob = _bytes_to_blob(blob)
    out_blob = DATA_BLOB()

    if not CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        flags,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()
    result = _blob_to_bytes(out_blob)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return result
