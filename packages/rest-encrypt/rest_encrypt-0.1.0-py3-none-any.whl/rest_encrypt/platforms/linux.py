# src/rest_encrypt/platforms/linux.py
from __future__ import annotations

"""Linux implementation of key wrapping using scrypt and AES-GCM."""

import json
import secrets
from dataclasses import dataclass
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HEADER = b"RENC\1"  # simple version tag


@dataclass
class ScryptParams:
    """Parameters used for the scrypt KDF."""

    salt: bytes
    n: int = 2**15
    r: int = 8
    p: int = 1
    key_len: int = 32


def _derive_key(password: bytes, params: ScryptParams) -> bytes:
    """Derive an AES key from ``password`` and ``params`` using scrypt."""

    kdf = Scrypt(
        salt=params.salt, length=params.key_len, n=params.n, r=params.r, p=params.p
    )
    return kdf.derive(password)


class ScryptWrapper:
    """
    Protect/unprotect small blobs using a local passphrase (root-only file) and AES-GCM.
    """

    def __init__(self, passphrase_path: str = "/etc/rest-encrypt/passphrase"):
        self.passphrase_path = passphrase_path

    def _load_passphrase(self) -> bytes:
        """Read the passphrase used for encryption."""
        with open(self.passphrase_path, "rb") as f:
            return f.read().strip()

    def protect(self, data: bytes) -> bytes:
        """Encrypt ``data`` using AES-GCM and return a wrapped blob."""
        pw = self._load_passphrase()
        params = ScryptParams(salt=secrets.token_bytes(16))
        key = _derive_key(pw, params)
        aes = AESGCM(key)
        nonce = secrets.token_bytes(12)
        ct = aes.encrypt(nonce, data, None)
        meta = {
            "salt": params.salt.hex(),
            "n": params.n,
            "r": params.r,
            "p": params.p,
            "nonce": nonce.hex(),
            "ct": ct.hex(),
        }
        return HEADER + json.dumps(meta).encode()

    def unprotect(self, blob: bytes) -> bytes:
        """Decrypt a blob previously produced by :meth:`protect`."""
        if not blob.startswith(HEADER):
            raise ValueError("Unknown blob header/version")
        meta = json.loads(blob[len(HEADER) :].decode())
        params = ScryptParams(
            salt=bytes.fromhex(meta["salt"]), n=meta["n"], r=meta["r"], p=meta["p"]
        )
        pw = self._load_passphrase()
        key = _derive_key(pw, params)
        aes = AESGCM(key)
        return aes.decrypt(
            bytes.fromhex(meta["nonce"]), bytes.fromhex(meta["ct"]), None
        )
