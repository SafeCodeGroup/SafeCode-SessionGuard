import os
import subprocess
from unittest import mock

import pytest

from sessionguard.inhibitor import SYSTEM, SleepInhibitor


def test_mac_runs_caffeinate_tied_to_our_pid():
    proc = mock.Mock()
    proc.poll.return_value = None
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
    proc.wait.side_effect = [subprocess.TimeoutExpired("caffeinate", 3), 0]
    with mock.patch.object(subprocess, "Popen", return_value=proc):
        inh = SleepInhibitor("Darwin")
        inh.start()
        inh.stop()
    proc.kill.assert_called_once()


def test_linux_falls_back_when_systemd_inhibit_missing():
    with mock.patch.object(subprocess, "Popen", side_effect=[FileNotFoundError, mock.Mock()]) as popen:
        assert SleepInhibitor("Linux").start()
    first, second = (c.args[0] for c in popen.call_args_list)
    assert first[0] == "systemd-inhibit" and "--who=SafeCode SessionGuard" in first
    assert second[0] == "caffeinate"
    # The held command watches our pid instead of sleeping forever.
    assert first[-3:-1] == ["sh", "-c"] and f"kill -0 {os.getpid()}" in first[-1]


@pytest.mark.skipif(SYSTEM == "Windows", reason="POSIX shell")
def test_linux_watcher_exits_when_parent_dies():
    import sys

    parent = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    watch = f"while kill -0 {parent.pid} 2>/dev/null; do sleep 0.2; done"
    child = subprocess.Popen(["sh", "-c", watch])
    parent.kill()
    parent.wait()
    assert child.wait(timeout=5) == 0


def test_unknown_platform_reports_failure():
    assert not SleepInhibitor("Plan9").start()


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
