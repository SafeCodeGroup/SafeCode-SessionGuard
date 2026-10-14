"""Rotating log file for support and crash diagnosis."""

import logging
import logging.handlers
import platform
import sys
import threading
from pathlib import Path

from . import APP_ID
from .settings import config_dir


def log_dir(system=None, home=None, env=None) -> Path:
    system = system or platform.system()
    if system == "Darwin":
        return (Path(home) if home else Path.home()) / "Library" / "Logs" / APP_ID
    return config_dir(system, env, home) / "logs"


def setup_logging(directory=None) -> Path:
    """Log to a rotating file and record any uncaught exception there."""
    directory = Path(directory or log_dir())
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "sessionguard.log"
    handler = logging.handlers.RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    log = logging.getLogger("sessionguard")
    previous_hook, previous_thread_hook = sys.excepthook, threading.excepthook

    def excepthook(exc_type, exc, tb):
        log.critical("Uncaught exception", exc_info=(exc_type, exc, tb))
        previous_hook(exc_type, exc, tb)  # keep the traceback on stderr too

    def thread_excepthook(args):
        log.critical(
            "Uncaught exception in thread %s",
            args.thread.name if args.thread else "?",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )
        previous_thread_hook(args)

    sys.excepthook = excepthook
    threading.excepthook = thread_excepthook
    return path
