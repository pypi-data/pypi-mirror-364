# src/rest_encrypt/store.py
"""High level interface for encrypted secret storage."""

from __future__ import annotations
import os
from pathlib import Path
from . import crypto
from .keywrap import get_wrapper
from .serializers import get as get_serializer


class SecretStore:
    """Manage encrypted secrets and the wrapped data key."""

    def __init__(
        self,
        secrets_path: str | Path,
        wrapped_key_path: str | Path,
        scope="user",
        wrapper=None,
        serializer: str = "json",
        passphrase_path: str | None = None,
    ) -> None:
        self.secrets_path = Path(secrets_path)
        self.wrapped_key_path = Path(wrapped_key_path)
        self.wrapper = wrapper or get_wrapper(scope, passphrase_path=passphrase_path)
        self.scope = scope
        self.serializer = get_serializer(serializer)

    # --- One-time init -------------------------------------------------------
    def init_from_plain(self, data: dict) -> None:
        """Initialise the store from a plaintext mapping of secrets."""
        raw_key = crypto.generate_key()
        wrapped = self.wrapper.protect(raw_key)
        cipher = crypto.encrypt(raw_key, self.serializer.dumps(data).encode("utf-8"))

        self.wrapped_key_path.write_bytes(wrapped)
        self.secrets_path.write_bytes(cipher)

        _zeroize(raw_key)

    # --- Load / decrypt -------------------------------------------------------
    def load(self) -> dict:
        """Return the decrypted secrets as a dictionary."""
        wrapped = self.wrapped_key_path.read_bytes()
        raw_key = self.wrapper.unprotect(wrapped)
        try:
            plaintext = crypto.decrypt(raw_key, self.secrets_path.read_bytes())
        finally:
            _zeroize(raw_key)
        return self.serializer.loads(plaintext.decode("utf-8"))

    def inject_env(self, data: dict | None = None, *, scope: str = "process") -> None:
        """Inject secrets into environment variables.

        Parameters
        ----------
        data:
            Mapping of secrets. If ``None``, the store is loaded first.
        scope:
            ``"process"`` (default) updates ``os.environ`` only. ``"user"`` or
            ``"machine"`` write to the Windows registry.
        """
        if data is None:
            data = self.load()

        if scope == "process":
            os.environ.update({k: str(v) for k, v in data.items()})
        elif scope in ("user", "machine"):
            target = "User" if scope == "user" else "Machine"
            for k, v in data.items():
                # Environment vars via registry
                import winreg

                root = (
                    winreg.HKEY_CURRENT_USER
                    if target == "User"
                    else winreg.HKEY_LOCAL_MACHINE
                )
                path = r"Environment"
                with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as h:
                    winreg.SetValueEx(h, k, 0, winreg.REG_SZ, str(v))
            # Broadcast change (optional)
            import ctypes

            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, None
            )
        else:
            raise ValueError("scope must be process|user|machine")

    # --- Rotation -------------------------------------------------------------
    def rotate_data_key(self) -> None:
        """Rotate the symmetric data key while keeping the secrets intact."""
        data = self.load()  # decrypt with old key
        self.init_from_plain(data)  # overwrites files with new key


def _zeroize(b: bytes) -> None:
    """Best-effort in-place overwrite of a bytes object."""
    # Best-effort overwrite (won't guarantee in CPython)
    try:
        mv = memoryview(b)
        for i in range(len(mv)):
            mv[i] = 0
    except Exception:
        pass
