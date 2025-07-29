import platform

if platform.system() == "Windows":  # pragma: no cover - platform specific
    from .windows import DPAPIWrapper, DPAPIScope
else:  # pragma: no cover - platform specific
    from enum import Enum

    class DPAPIScope(str, Enum):  # type: ignore
        USER = "user"
        MACHINE = "machine"

    DPAPIWrapper = None  # type: ignore

from .linux import ScryptWrapper

__all__ = [
    "DPAPIWrapper",
    "DPAPIScope",
    "ScryptWrapper",
]
