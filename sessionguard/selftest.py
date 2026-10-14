"""Startup self-test: load every runtime dependency the way the app uses it.

Run a built binary with `--self-test <report-file>` to check that packaging
included everything for this platform (tray backend with menus, input
backends, OS APIs). Exit code 0 = all good.
"""

import importlib
import platform

SYSTEM = platform.system()


def run_checks(system: str = SYSTEM) -> list:
    """Return a list of human-readable problems (empty if everything loads)."""
    from .compat import ensure_gobject_idle_add

    problems = []

    def check(name, fn):
        try:
            fn()
        except Exception as exc:  # report every failure, keep going
            problems.append(f"{name}: {type(exc).__name__}: {exc}")

    def tray():
        ensure_gobject_idle_add()
        import pystray

        backend = pystray.Icon.__module__
        expected = {"Darwin": "pystray._darwin", "Windows": "pystray._win32"}.get(
            system, "pystray._appindicator"
        )
        if backend != expected:
            raise RuntimeError(f"tray backend is {backend}, expected {expected} (menus need it)")

    check("tray", tray)
    check("mouse input", lambda: importlib.import_module("pynput.mouse").Controller())
    check("keyboard input", lambda: importlib.import_module("pynput.keyboard").Controller())
    check("icon artwork", lambda: importlib.import_module("sessionguard.icon").create_icon_image("active"))

    if system == "Darwin":
        check(
            "idle time (Quartz)",
            lambda: importlib.import_module("Quartz").CGEventSourceSecondsSinceLastEventType,
        )
        check("accessibility (HIServices)", lambda: importlib.import_module("HIServices").AXIsProcessTrusted)
        check("main-thread dispatch", lambda: importlib.import_module("PyObjCTools.AppHelper").callAfter)
    elif system == "Windows":

        def win_apis():
            import ctypes

            for dll, fn in (
                ("user32", "SendInput"),
                ("user32", "GetLastInputInfo"),
                ("kernel32", "SetThreadExecutionState"),
            ):
                getattr(getattr(ctypes.windll, dll), fn)  # raises if missing

        check("Windows APIs", win_apis)
        check("registry", lambda: importlib.import_module("winreg"))
    elif system == "Linux":

        def gobject():
            from gi.repository import GObject

            if not callable(getattr(GObject, "idle_add", None)):
                raise RuntimeError("GObject.idle_add missing")

        check("GObject.idle_add", gobject)
    return problems


def write_report(path) -> int:
    problems = run_checks()
    text = "OK\n" if not problems else "FAILED\n" + "\n".join(problems) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{platform.platform()}\n{text}")
    return 1 if problems else 0
