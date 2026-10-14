"""Imperceptible input nudges so the session never looks idle."""

import logging
import platform
import threading
import time

from .idle import idle_seconds

log = logging.getLogger(__name__)
SYSTEM = platform.system()


def nudge_key_name(system: str = SYSTEM) -> str:
    """pynput Key member to tap.

    F15 exists on every OS and does nothing, but macOS maps F14/F15 to
    display brightness by default, so a lone Shift tap is used there instead.
    """
    return "shift" if system == "Darwin" else "f15"


KEY_LABEL = nudge_key_name().capitalize() if SYSTEM == "Darwin" else nudge_key_name().upper()


def windows_mouse_move(dx: int, dy: int) -> None:
    """Relative mouse move via SendInput.

    Unlike SetCursorPos (what pynput uses), SendInput counts as user input,
    so it resets the idle timer that screen lock and presence apps read.
    """
    import ctypes

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_int32),
            ("dy", ctypes.c_int32),
            ("mouseData", ctypes.c_uint32),
            ("dwFlags", ctypes.c_uint32),
            ("time", ctypes.c_uint32),
            ("dwExtraInfo", ctypes.c_size_t),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_uint16),
            ("wScan", ctypes.c_uint16),
            ("dwFlags", ctypes.c_uint32),
            ("time", ctypes.c_uint32),
            ("dwExtraInfo", ctypes.c_size_t),
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_uint32), ("wParamL", ctypes.c_uint16), ("wParamH", ctypes.c_uint16)]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_uint32), ("u", _INPUTUNION)]

    INPUT_MOUSE, MOUSEEVENTF_MOVE = 0, 0x0001
    event = INPUT(type=INPUT_MOUSE, u=_INPUTUNION(mi=MOUSEINPUT(dx=dx, dy=dy, dwFlags=MOUSEEVENTF_MOVE)))
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
        raise OSError(ctypes.get_last_error(), "SendInput failed")


class KeepAlive:
    """Nudges the mouse or keyboard every `settings.interval` seconds.

    With `settings.idle_only`, nudges happen only once the user has been
    idle for at least one interval. Settings are read live on every poll.
    """

    POLL = 5.0

    def __init__(
        self, settings, idle_fn=idle_seconds, mouse=None, keyboard=None, system=SYSTEM, clock=time.monotonic
    ):
        self.settings = settings
        self._idle_fn = idle_fn
        self._mouse = mouse
        self._keyboard = keyboard
        self._system = system
        self._clock = clock
        self._last = clock()
        self._running = False
        self._thread = None
        self._wake = None
        self._failing = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._last = self._clock()
        # A fresh event per run: a previous loop that is still stuck in a slow
        # nudge keeps its own (set) event and exits instead of running twice.
        self._wake = threading.Event()
        self._thread = threading.Thread(target=self._loop, args=(self._wake,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._wake is not None:
            self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None

    def due(self, now: float) -> bool:
        interval = self.settings.interval
        if self.settings.method == "none" or now - self._last < interval:
            return False
        if self.settings.idle_only:
            idle = self._idle_fn()
            if idle is not None and idle < interval:
                return False
        return True

    def nudge(self) -> None:
        method = self.settings.method
        if method == "mouse":
            self._move_mouse(1, 0)
            time.sleep(0.05)
            self._move_mouse(-1, 0)
        elif method == "key":
            from pynput.keyboard import Key

            key = getattr(Key, nudge_key_name(self._system))
            keyboard = self._get_keyboard()
            keyboard.press(key)
            keyboard.release(key)

    def _move_mouse(self, dx: int, dy: int) -> None:
        if self._system == "Windows" and self._mouse is None:
            windows_mouse_move(dx, dy)
        else:
            self._get_mouse().move(dx, dy)

    def _get_mouse(self):
        if self._mouse is None:
            from pynput.mouse import Controller

            self._mouse = Controller()
        return self._mouse

    def _get_keyboard(self):
        if self._keyboard is None:
            from pynput.keyboard import Controller

            self._keyboard = Controller()
        return self._keyboard

    def _loop(self, wake: threading.Event) -> None:
        while not wake.wait(min(self.POLL, self.settings.interval)):
            now = self._clock()
            if not self.due(now):
                continue
            try:
                self.nudge()
                self._failing = False
            except Exception:
                # Input may be blocked (e.g. missing Accessibility permission);
                # keep the sleep inhibitor running regardless. Log once per streak.
                if not self._failing:
                    log.warning("Input nudge failed", exc_info=True)
                self._failing = True
            self._last = now
