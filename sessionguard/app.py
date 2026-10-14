"""Tray / menu-bar UI."""

import logging
import os
import platform
import subprocess
import threading
import webbrowser

from . import APP_ID, APP_NAME, HOMEPAGE, __version__
from .autostart import Autostart
from .guard import Guard
from .icon import create_icon_image
from .inhibitor import SleepInhibitor
from .instance import SingleInstance
from .keepalive import KEY_LABEL, KeepAlive
from .logs import setup_logging
from .permissions import input_allowed, request_input_permission
from .schedule import describe
from .settings import DURATIONS, INTERVALS, config_dir, default_settings_path, load, save

log = logging.getLogger(__name__)

SYSTEM = platform.system()
PLATFORM_LABEL = {"Darwin": "macOS"}.get(SYSTEM, SYSTEM)
METHOD_LABELS = {
    "mouse": "Mouse jiggle",
    "key": f"Key press ({KEY_LABEL})",
    "none": "Prevent sleep only",
}


def duration_label(minutes: int) -> str:
    if minutes == 0:
        return "No time limit"
    if minutes % 60 == 0:
        hours = minutes // 60
        return f"{hours} hour" + ("s" if hours > 1 else "")
    return f"{minutes} minutes"


def call_on_main(fn) -> None:
    """Run fn on the UI thread. macOS aborts on AppKit calls from other threads."""
    if SYSTEM == "Darwin":
        from PyObjCTools import AppHelper

        AppHelper.callAfter(fn)
    else:
        fn()


def open_path(path) -> None:
    if SYSTEM == "Windows":
        os.startfile(path)
    elif SYSTEM == "Darwin":
        subprocess.Popen(["open", "-t", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class SessionGuardApp:
    TICK = 15  # seconds between time-limit / active-hours checks

    def __init__(self, settings_path=None, inhibitor=None, keepalive=None, autostart=None):
        self.settings_path = settings_path or default_settings_path()
        self.settings = load(self.settings_path)
        self.keepalive = keepalive or KeepAlive(self.settings)
        self.guard = Guard(self.settings, inhibitor or SleepInhibitor(), self.keepalive)
        self.autostart = autostart or Autostart()
        self.icon = None
        self._stopping = threading.Event()

    # Menu ---------------------------------------------------------------

    def _build_menu(self):
        from pystray import Menu, MenuItem

        def radio(label, attr, value, on_change=None):
            def select(icon, item):
                setattr(self.settings, attr, value)
                self._save()
                if on_change:
                    on_change()
                self._refresh()

            return MenuItem(
                label, select, checked=lambda item: getattr(self.settings, attr) == value, radio=True
            )

        def toggle(label, attr, on_change=None):
            def flip(icon, item):
                setattr(self.settings, attr, not getattr(self.settings, attr))
                self._save()
                if on_change:
                    on_change()
                self._refresh()

            return MenuItem(label, flip, checked=lambda item: getattr(self.settings, attr))

        restart_timer = lambda: self.guard.armed and self.guard.arm()

        return Menu(
            MenuItem(
                lambda item: "⏸ Stop Guard" if self.guard.armed else "▶ Start Guard",
                self._toggle,
                default=True,
            ),
            MenuItem(lambda item: self.guard.status_text(), None, enabled=False),
            MenuItem(
                "⚠ Allow input in Accessibility settings…",
                lambda icon, item: request_input_permission(),
                visible=lambda item: self.settings.method != "none" and not input_allowed(),
            ),
            Menu.SEPARATOR,
            MenuItem(
                "Keep awake for",
                Menu(*(radio(duration_label(m), "duration", m, restart_timer) for m in DURATIONS)),
            ),
            MenuItem("Method", Menu(*(radio(label, "method", m) for m, label in METHOD_LABELS.items()))),
            MenuItem("Interval", Menu(*(radio(f"{s} seconds", "interval", s) for s in INTERVALS))),
            toggle("Only when idle", "idle_only"),
            toggle(
                lambda item: (
                    "Active hours ("
                    + describe(
                        self.settings.schedule_start,
                        self.settings.schedule_end,
                        self.settings.schedule_days,
                    )
                    + ")"
                ),
                "schedule_enabled",
                self.guard.evaluate,
            ),
            MenuItem(
                "Launch at login",
                self._toggle_autostart,
                checked=lambda item: self.autostart.is_enabled(),
            ),
            Menu.SEPARATOR,
            MenuItem("Edit settings…", self._edit_settings),
            MenuItem("Reload settings", self._reload_settings),
            MenuItem(f"{APP_NAME} {__version__} · {PLATFORM_LABEL}", None, enabled=False),
            MenuItem("Visit safecodeg.com", lambda icon, item: webbrowser.open(HOMEPAGE)),
            MenuItem("Quit", self._quit),
        )

    # Actions ------------------------------------------------------------

    def _toggle(self, icon=None, item=None):
        if self.guard.armed:
            self.guard.disarm()
        else:
            self.guard.arm()
        self._refresh()

    def _toggle_autostart(self, icon=None, item=None):
        if self.autostart.is_enabled():
            self.autostart.disable()
        else:
            self.autostart.enable()
        self._refresh()

    def _edit_settings(self, icon=None, item=None):
        self._save()
        open_path(self.settings_path)

    def _reload_settings(self, icon=None, item=None):
        self.settings.update_from(load(self.settings_path))
        self.guard.evaluate()
        self._refresh()

    def _save(self):
        save(self.settings, self.settings_path)

    def _refresh(self):
        if self.icon is None:
            return
        self.icon.icon = create_icon_image(self.guard.status)
        self.icon.title = self._title()
        self.icon.update_menu()

    def _title(self) -> str:
        return f"{APP_NAME} — {self.guard.status_text()}"

    def _quit(self, icon=None, item=None):
        self._stopping.set()
        self.guard.disarm()
        if self.icon is not None:
            self.icon.stop()

    # Lifecycle ----------------------------------------------------------

    def _tick_loop(self):
        while not self._stopping.wait(self.TICK):
            if self.guard.evaluate():
                call_on_main(self._refresh)

    def run(self):
        import pystray

        # Start before the tray loop: on macOS, tray updates from a
        # non-main thread abort the process (SIGTRAP).
        if self.settings.start_on_launch:
            self.guard.arm()
        self.icon = pystray.Icon(
            APP_ID,
            create_icon_image(self.guard.status),
            self._title(),
            menu=self._build_menu(),
        )
        threading.Thread(target=self._tick_loop, daemon=True).start()
        try:
            self.icon.run()
        finally:
            self._stopping.set()
            self.guard.disarm()


def main() -> int:
    log_path = setup_logging()
    instance = SingleInstance(config_dir() / "instance.lock")
    if not instance.acquire():
        log.info("Another instance is already running; exiting")
        return 0
    log.info("%s %s starting on %s (log: %s)", APP_NAME, __version__, platform.platform(), log_path)
    try:
        SessionGuardApp().run()
    finally:
        log.info("Exited")
        instance.release()
    return 0
