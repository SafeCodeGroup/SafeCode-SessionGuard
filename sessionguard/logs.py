"""Rotating log file for support and crash diagnosis."""

import logging
import logging.handlers
import platform
import sys
import threading
from pathlib import Path

from . import APP_ID
from .settings import config_dir


def log_dir(system=None, home=None) -> Path:
    system = system or platform.system()
    if system == "Darwin":
        return (Path(home) if home else Path.home()) / "Library" / "Logs" / APP_ID
    return config_dir(system, None, home) / "logs"


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

    def excepthook(exc_type, exc, tb):
        logging.getLogger("sessionguard").critical("Uncaught exception", exc_info=(exc_type, exc, tb))

    sys.excepthook = excepthook
    threading.excepthook = lambda a: excepthook(a.exc_type, a.exc_value, a.exc_traceback)
    return path
