"""Public API for the :mod:`rest_encrypt` package.

The :class:`~rest_encrypt.store.SecretStore` class is the main entry point for
reading and writing encrypted secrets.  The :func:`~rest_encrypt.keywrap.get_wrapper`
helper returns the platform specific key wrapper used internally.
"""

from .store import SecretStore
from .keywrap import get_wrapper, KeyWrapper

__all__ = ["SecretStore", "get_wrapper", "KeyWrapper"]
