import time

from sessionguard.keepalive import KeepAlive
from sessionguard.settings import Settings
from tests.fakes import Clock, FakeKeyboard, FakeMouse


def make(idle=None, **kw):
    clock = Clock(1000.0)
    ka = KeepAlive(
        Settings(**kw), idle_fn=lambda: idle, mouse=FakeMouse(), keyboard=FakeKeyboard(), clock=clock
    )
    return ka, clock


def test_not_due_before_interval():
    ka, clock = make(interval=60, idle_only=False)
    assert not ka.due(clock.now + 59)
    assert ka.due(clock.now + 60)


def test_idle_only_waits_for_user_to_be_away():
    ka, clock = make(idle=10, interval=60)
    assert not ka.due(clock.now + 120)
    ka._idle_fn = lambda: 75
    assert ka.due(clock.now + 120)


def test_idle_unknown_falls_back_to_timer():
    ka, clock = make(idle=None, interval=60)
    assert ka.due(clock.now + 60)


def test_method_none_never_nudges():
    ka, clock = make(method="none", idle_only=False)
    assert not ka.due(clock.now + 10_000)


def test_mouse_nudge_returns_cursor():
    ka, _ = make(method="mouse")
    ka.nudge()
    assert ka._mouse.moves == [(1, 0), (-1, 0)]


def test_key_nudge_presses_and_releases_harmless_key():
    from pynput.keyboard import Key

    ka, _ = make(method="key")
    ka._system = "Windows"
    ka.nudge()
    assert ka._keyboard.events == [("press", Key.f15), ("release", Key.f15)]
    ka._keyboard.events.clear()
    ka._system = "Darwin"
    ka.nudge()
    assert ka._keyboard.events == [("press", Key.shift), ("release", Key.shift)]


def test_loop_nudges_and_stops_promptly():
    ka = KeepAlive(Settings(interval=5, idle_only=False), mouse=FakeMouse())
    ka.settings.interval = 0.05  # bypass validation for a fast test
    ka.start()
    time.sleep(0.5)
    t0 = time.monotonic()
    ka.stop()
    assert time.monotonic() - t0 < 1
    assert not ka.running
    assert len(ka._mouse.moves) >= 2
