"""Launch at login: LaunchAgent (macOS), Run key (Windows), XDG autostart (Linux)."""

import logging
import os
import platform
import plistlib
import shlex
import subprocess
import sys
from pathlib import Path

from . import APP_ID, APP_NAME, BUNDLE_ID

log = logging.getLogger(__name__)
SYSTEM = platform.system()
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def launch_command() -> list:
    if getattr(sys, "frozen", False):
        return [sys.executable]
    script = Path(__file__).resolve().parent.parent / "session_guard.py"
    python = Path(sys.executable)
    windowless = python.with_name("pythonw.exe")  # no console window at login
    if SYSTEM == "Windows" and windowless.exists():
        python = windowless
    return [str(python), str(script)]


def is_temporary_location(path: str) -> bool:
    """macOS runs quarantined apps from a randomized copy, and DMGs are
    unmounted after reboot; neither path is usable for launch at login."""
    return "/AppTranslocation/" in path or path.startswith("/Volumes/")


def _winreg():
    import winreg

    return winreg


class Autostart:
    def __init__(self, system=SYSTEM, home=None, env=None, command=None, winreg=None):
        self.system = system
        self.home = Path(home) if home else Path.home()
        self.env = os.environ if env is None else env
        self.command = command or launch_command()
        self._winreg = winreg

    @property
    def path(self) -> Path:
        if self.system == "Darwin":
            return self.home / "Library" / "LaunchAgents" / f"{BUNDLE_ID}.plist"
        config = Path(self.env.get("XDG_CONFIG_HOME") or self.home / ".config")
        return config / "autostart" / "safecode-sessionguard.desktop"

    def is_enabled(self) -> bool:
        if self.system == "Windows":
            return self._read_run_key() is not None
        return self.path.exists()

    def enable(self) -> bool:
        """Returns False if the app must be moved to a permanent location first."""
        if self.system == "Darwin" and is_temporary_location(self.command[0]):
            log.warning("Not enabling launch at login from temporary path %s", self.command[0])
            return False
        if self.system == "Windows":
            reg = self._winreg or _winreg()
            with reg.CreateKey(reg.HKEY_CURRENT_USER, RUN_KEY) as key:
                reg.SetValueEx(key, APP_ID, 0, reg.REG_SZ, subprocess.list2cmdline(self.command))
            return True
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.system == "Darwin":
            plist = {
                "Label": BUNDLE_ID,
                "ProgramArguments": self.command,
                "RunAtLoad": True,
                "ProcessType": "Interactive",
            }
            with open(self.path, "wb") as f:
                plistlib.dump(plist, f)
        else:
            self.path.write_text(
                "[Desktop Entry]\n"
                "Type=Application\n"
                f"Name={APP_NAME}\n"
                f"Exec={shlex.join(self.command)}\n"
                "X-GNOME-Autostart-enabled=true\n",
                encoding="utf-8",
            )
        return True

    def disable(self) -> None:
        if self.system == "Windows":
            reg = self._winreg or _winreg()
            try:
                with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY, 0, reg.KEY_SET_VALUE) as key:
                    reg.DeleteValue(key, APP_ID)
            except FileNotFoundError:
                pass
            return
        self.path.unlink(missing_ok=True)

    def _read_run_key(self):
        reg = self._winreg or _winreg()
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, RUN_KEY) as key:
                return reg.QueryValueEx(key, APP_ID)[0]
        except FileNotFoundError:
            return None
