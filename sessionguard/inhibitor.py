"""OS-native sleep prevention."""

import logging
import os
import platform
import subprocess

from . import APP_NAME

log = logging.getLogger(__name__)

SYSTEM = platform.system()


class SleepInhibitor:
    """Prevents system sleep using OS-native mechanisms."""

    def __init__(self, system: str = SYSTEM):
        self.system = system
        self._proc = None
        self._es = None

    @property
    def active(self) -> bool:
        return self._proc is not None or self._es is not None

    def start(self) -> bool:
        if self.active:
            return True
        starters = {
            "Darwin": self._start_mac,
            "Windows": self._start_windows,
            "Linux": self._start_linux,
        }
        ok = starters[self.system]() if self.system in starters else False
        if not ok:
            log.warning("Sleep prevention unavailable on %s", self.system)
        return ok

    def stop(self) -> None:
        if self._proc is not None:
            self._stop_subprocess()
        if self._es is not None:
            self._stop_windows()

    def _spawn(self, cmd) -> bool:
        try:
            self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            self._proc = None
            return False

    def _start_mac(self) -> bool:
        # -d display, -i idle, -m disk, -s system (on AC power).
        # -w ties caffeinate to this process so it exits if we crash.
        return self._spawn(["caffeinate", "-dims", "-w", str(os.getpid())])

    def _start_windows(self) -> bool:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        try:
            import ctypes

            flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            if not ctypes.windll.kernel32.SetThreadExecutionState(flags):
                return False
            self._es = flags
            return True
        except Exception:
            return False

    def _start_linux(self) -> bool:
        # The inhibitor holds its lock while this child runs; the child exits
        # once we do, so a crash never leaves sleep blocked.
        watch = ["sh", "-c", f"while kill -0 {os.getpid()} 2>/dev/null; do sleep 5; done"]
        cmds = [
            [
                "systemd-inhibit",
                "--what=idle:sleep",
                f"--who={APP_NAME}",
                "--why=Keeping session alive",
                "--mode=block",
                *watch,
            ],
            ["caffeinate", *watch],
        ]
        return any(self._spawn(cmd) for cmd in cmds)

    def _stop_subprocess(self) -> None:
        proc, self._proc = self._proc, None
        if proc.poll() is not None:
            return
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    def _stop_windows(self) -> None:
        ES_CONTINUOUS = 0x80000000
        try:
            import ctypes

            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        except Exception:
            pass
        self._es = None
