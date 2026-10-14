"""Seconds since the user last touched the keyboard or mouse."""

import platform
import subprocess

SYSTEM = platform.system()


def idle_seconds(system: str = SYSTEM):
    """Return idle time in seconds, or None if it can't be determined."""
    try:
        if system == "Darwin":
            return _idle_mac()
        if system == "Windows":
            return _idle_windows()
        if system == "Linux":
            return _idle_linux()
    except Exception:
        pass
    return None


def _idle_mac() -> float:
    import Quartz

    return float(
        Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateHIDSystemState, Quartz.kCGAnyInputEventType
        )
    )


def _idle_windows():
    import ctypes

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        return None
    # Both are 32-bit tick counts; mask handles the 49.7-day wraparound.
    millis = (ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF
    return millis / 1000.0


def _idle_linux():
    # X11 only; Wayland has no portable idle query, so we fall back to None.
    try:
        out = subprocess.run(["xprintidle"], capture_output=True, text=True, timeout=2, check=True).stdout
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return int(out.strip()) / 1000.0
