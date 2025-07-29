# src/rest_encrypt/keywrap.py
"""Abstraction for protecting symmetric keys on different platforms."""

from __future__ import annotations

import platform
from typing import Protocol

from .platforms import DPAPIWrapper, DPAPIScope, ScryptWrapper


class KeyWrapper(Protocol):
    """Simple interface for wrapping and unwrapping symmetric keys."""

    def protect(self, data: bytes) -> bytes:
        """Encrypt ``data`` and return a wrapped blob."""

    def unprotect(self, blob: bytes) -> bytes:
        """Decrypt a blob previously returned by :meth:`protect`."""


def get_wrapper(
    scope: str = DPAPIScope.USER,
    *,
    passphrase_path: str | None = None,
) -> KeyWrapper:
    """Return the platform-appropriate :class:`KeyWrapper` implementation.

    Parameters
    ----------
    scope:
        DPAPI scope on Windows.  Ignored on Linux.
    passphrase_path:
        Path to the passphrase file used by :class:`ScryptWrapper` on Linux.
    """

    if platform.system() == "Windows":
        return DPAPIWrapper(scope=scope)

    return ScryptWrapper(
        passphrase_path=passphrase_path or "/etc/rest-encrypt/passphrase"
    )
