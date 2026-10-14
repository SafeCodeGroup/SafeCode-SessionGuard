"""Regression tests for cross-platform fixes."""

import ctypes
import sys
import time
import types

import pytest

from sessionguard import autostart, compat, keepalive
from sessionguard.app import SessionGuardApp
from sessionguard.keepalive import KeepAlive, nudge_key_name
from sessionguard.settings import Settings, load
from tests.fakes import FakeComponent


def test_gobject_idle_add_shim(monkeypatch):
    class Module:  # stands in for gi.repository.GObject without idle_add
        pass

    glib, gobject = types.SimpleNamespace(idle_add=lambda *a: "queued"), Module()
    repo = types.SimpleNamespace(GLib=glib, GObject=gobject)
    monkeypatch.setitem(sys.modules, "gi", types.SimpleNamespace(repository=repo))
    monkeypatch.setitem(sys.modules, "gi.repository", repo)
    compat.ensure_gobject_idle_add()
    assert gobject.idle_add() == "queued"


def test_gobject_shim_without_pygobject_is_noop(monkeypatch):
    monkeypatch.setitem(sys.modules, "gi", None)
    compat.ensure_gobject_idle_add()


def test_nudge_key_per_platform():
    assert nudge_key_name("Darwin") == "shift"
    assert nudge_key_name("Windows") == nudge_key_name("Linux") == "f15"


def test_windows_mouse_uses_sendinput(monkeypatch):
    moves = []
    monkeypatch.setattr(keepalive, "windows_mouse_move", lambda dx, dy: moves.append((dx, dy)))
    ka = KeepAlive(Settings(method="mouse"), system="Windows")
    ka.nudge()
    assert moves == [(1, 0), (-1, 0)]


@pytest.mark.skipif(ctypes.sizeof(ctypes.c_void_p) != 8, reason="64-bit layout")
def test_windows_input_struct_layout(monkeypatch):
    # sizeof(INPUT) must be 40 on 64-bit Windows or SendInput rejects it.
    sizes = []

    class FakeUser32:
        def SendInput(self, n, ptr, size):
            sizes.append(size)
            return 1

    monkeypatch.setattr(ctypes, "WinDLL", lambda *a, **k: FakeUser32(), raising=False)
    keepalive.windows_mouse_move(1, 0)
    assert sizes == [40]


def test_restart_never_leaves_two_loops():
    class SlowMouse:
        def __init__(self):
            self.moves = 0

        def move(self, dx, dy):
            self.moves += 1
            time.sleep(0.3)

    ka = KeepAlive(Settings(idle_only=False), mouse=SlowMouse())
    ka.settings.interval = 0.01
    ka.start()
    first = ka._thread
    time.sleep(0.05)
    ka.stop()
    ka.start()
    second = ka._thread
    time.sleep(1.0)
    ka.stop()
    first.join(2)
    assert not first.is_alive() and not second.is_alive()


def test_settings_with_utf8_bom(tmp_path):
    path = tmp_path / "settings.json"
    path.write_bytes(b'\xef\xbb\xbf{"interval": 120}')
    assert load(path).interval == 120


def test_autostart_refuses_temporary_mac_paths(tmp_path):
    for path in (
        "/private/var/folders/x/AppTranslocation/ABC/d/SafeCode SessionGuard.app/Contents/MacOS/x",
        "/Volumes/SafeCode SessionGuard/SafeCode SessionGuard.app/Contents/MacOS/x",
    ):
        a = autostart.Autostart("Darwin", home=tmp_path, command=[path])
        assert a.enable() is False and not a.is_enabled()


def test_autostart_enable_reports_success(tmp_path):
    cmd = ["/Applications/SafeCode SessionGuard.app/Contents/MacOS/SafeCodeSessionGuard"]
    assert autostart.Autostart("Darwin", home=tmp_path, command=cmd).enable() is True


def test_post_refresh_without_window_falls_back(tmp_path):
    app = SessionGuardApp(
        settings_path=tmp_path / "s.json", inhibitor=FakeComponent(), keepalive=FakeComponent()
    )
    assert app._post_refresh() is False
