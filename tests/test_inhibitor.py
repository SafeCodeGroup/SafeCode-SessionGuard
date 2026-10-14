import os
import subprocess
import sys
import threading
from unittest import mock

import pytest

from sessionguard import inhibitor as inh_mod
from sessionguard.inhibitor import SYSTEM, SleepInhibitor


def running_proc():
    """A Popen stand-in that is still running when start() checks on it."""
    proc = mock.Mock()
    proc.poll.return_value = None
    proc.wait.side_effect = [subprocess.TimeoutExpired("x", 0.3), 0]
    return proc


def exited_proc(code=1):
    proc = mock.Mock()
    proc.wait.return_value = code
    return proc


def test_mac_runs_caffeinate_tied_to_our_pid():
    proc = running_proc()
    with mock.patch.object(subprocess, "Popen", return_value=proc) as popen:
        inh = SleepInhibitor("Darwin")
        assert inh.start() and inh.active
        assert popen.call_args.args[0] == ["caffeinate", "-dims", "-w", str(os.getpid())]
        inh.stop()
    proc.terminate.assert_called_once()
    assert not inh.active


def test_stop_kills_process_that_ignores_terminate():
    proc = mock.Mock()
    proc.poll.return_value = None
    proc.wait.side_effect = [
        subprocess.TimeoutExpired("x", 0.3),  # start(): still running
        subprocess.TimeoutExpired("x", 3),  # stop(): ignores terminate
        0,
    ]
    with mock.patch.object(subprocess, "Popen", return_value=proc):
        inh = SleepInhibitor("Darwin")
        inh.start()
        inh.stop()
    proc.kill.assert_called_once()


def test_linux_falls_back_when_systemd_inhibit_missing():
    with mock.patch.object(subprocess, "Popen", side_effect=[FileNotFoundError, running_proc()]) as popen:
        assert SleepInhibitor("Linux").start()
    first, second = (c.args[0] for c in popen.call_args_list)
    assert first[0] == "systemd-inhibit" and "--who=SafeCode SessionGuard" in first
    assert second[0] == "caffeinate"
    # The held command watches our pid instead of sleeping forever.
    assert first[-3:-1] == ["sh", "-c"] and f"kill -0 {os.getpid()}" in first[-1]


def test_helper_that_exits_immediately_is_not_active():
    # e.g. polkit refuses systemd-inhibit; fall through to the next helper.
    with mock.patch.object(subprocess, "Popen", side_effect=[exited_proc(1), exited_proc(127)]):
        inh = SleepInhibitor("Linux")
        assert not inh.start()
    assert not inh.active


def test_unknown_platform_reports_failure():
    assert not SleepInhibitor("Plan9").start()


def test_windows_state_set_and_cleared_on_same_thread(monkeypatch):
    calls = []
    monkeypatch.setattr(
        inh_mod, "_set_execution_state", lambda flags: calls.append((threading.get_ident(), flags)) or True
    )
    inh = SleepInhibitor("Windows")
    assert inh.start() and inh.active
    # Stop from a different thread than start, as the tick thread does.
    t = threading.Thread(target=inh.stop)
    t.start()
    t.join()
    assert not inh.active
    (set_thread, set_flags), (clear_thread, clear_flags) = calls
    assert set_thread == clear_thread != threading.get_ident()
    assert set_flags == inh_mod.ES_CONTINUOUS | inh_mod.ES_SYSTEM_REQUIRED | inh_mod.ES_DISPLAY_REQUIRED
    assert clear_flags == inh_mod.ES_CONTINUOUS


def test_windows_failure_reports_inactive(monkeypatch):
    monkeypatch.setattr(inh_mod, "_set_execution_state", lambda flags: False)
    inh = SleepInhibitor("Windows")
    assert not inh.start() and not inh.active


@pytest.mark.skipif(SYSTEM == "Windows", reason="POSIX shell")
def test_linux_watcher_exits_when_parent_dies():
    parent = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    watch = f"while kill -0 {parent.pid} 2>/dev/null; do sleep 0.2; done"
    child = subprocess.Popen(["sh", "-c", watch])
    parent.kill()
    parent.wait()
    assert child.wait(timeout=5) == 0


@pytest.mark.skipif(SYSTEM != "Darwin", reason="macOS only")
def test_real_caffeinate_lifecycle():
    inh = SleepInhibitor()
    assert inh.start()
    proc = inh._proc
    assert proc.poll() is None
    inh.stop()
    assert proc.poll() is not None


@pytest.mark.skipif(SYSTEM != "Windows", reason="Windows only")
def test_real_execution_state():
    inh = SleepInhibitor()
    assert inh.start() and inh.active
    inh.stop()
    assert not inh.active
