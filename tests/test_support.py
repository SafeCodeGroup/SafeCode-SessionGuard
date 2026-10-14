"""Single-instance lock, logging and permission helpers."""

import logging
import sys
import threading
from pathlib import Path

from sessionguard import permissions
from sessionguard.instance import SingleInstance
from sessionguard.logs import log_dir, setup_logging


def test_second_instance_is_refused_until_first_releases(tmp_path):
    lock = tmp_path / "instance.lock"
    first, second = SingleInstance(lock), SingleInstance(lock)
    assert first.acquire()
    assert not second.acquire()
    first.release()
    assert second.acquire()
    second.release()


def test_log_dir_per_platform():
    home = Path("/home/u")
    assert log_dir("Darwin", home) == home / "Library/Logs/SafeCodeSessionGuard"
    assert log_dir("Linux", home) == home / ".config/SafeCodeSessionGuard/logs"


def test_setup_logging_writes_file_and_captures_crashes(tmp_path):
    root = logging.getLogger()
    before = list(root.handlers), sys.excepthook, threading.excepthook
    try:
        path = setup_logging(tmp_path)
        logging.getLogger("sessionguard.test").info("hello")
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            sys.excepthook(*sys.exc_info())
        for h in root.handlers:
            h.flush()
        text = path.read_text()
        assert "hello" in text and "Uncaught exception" in text and "RuntimeError: boom" in text
    finally:
        for h in root.handlers[len(before[0]) :]:
            h.close()
        root.handlers[:] = before[0]
        sys.excepthook = before[1]
        threading.excepthook = before[2]


def test_permissions_are_noops_off_macos():
    assert permissions.input_allowed("Linux") is True
    assert permissions.request_input_permission("Windows") is None
