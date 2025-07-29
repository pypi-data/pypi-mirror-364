# src/rest_encrypt/crypto.py
"""Small Fernet wrapper used for encrypting and decrypting secrets."""

from cryptography.fernet import Fernet, InvalidToken

HEADER = b"RENC\x01"


def generate_key() -> bytes:
    """Return a new random 32 byte encryption key."""
    return Fernet.generate_key()


def encrypt(key: bytes, data: bytes) -> bytes:
    """Encrypt ``data`` with ``key`` and prepend a version header."""
    token = Fernet(key).encrypt(data)
    return HEADER + token


def decrypt(key: bytes, token: bytes) -> bytes:
    """Decrypt a token created by :func:`encrypt`."""

    if not token.startswith(HEADER):
        raise ValueError("Unknown file header/version")
    real_token = token[len(HEADER) :]
    try:
        return Fernet(key).decrypt(real_token)
    except InvalidToken as e:
        raise ValueError("Decryption failed (bad key or corrupted file).") from e
