"""Imperceptible input nudges so the session never looks idle."""

import logging
import platform
import threading
import time

from .idle import idle_seconds

log = logging.getLogger(__name__)
SYSTEM = platform.system()
# F15 exists on every OS and does nothing, but macOS maps F14/F15 to
# display brightness by default, so a lone Shift tap is used there instead.
KEY_LABEL = "Shift" if SYSTEM == "Darwin" else "F15"


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
        self._wake = threading.Event()
        self._failing = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._last = self._clock()
        self._wake.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
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
            mouse = self._get_mouse()
            mouse.move(1, 0)
            time.sleep(0.05)
            mouse.move(-1, 0)
        elif method == "key":
            from pynput.keyboard import Key

            key = Key.shift if self._system == "Darwin" else Key.f15
            keyboard = self._get_keyboard()
            keyboard.press(key)
            keyboard.release(key)

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

    def _loop(self) -> None:
        while not self._wake.wait(min(self.POLL, self.settings.interval)):
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
