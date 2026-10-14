import datetime

from sessionguard.guard import Guard
from sessionguard.settings import Settings
from tests.fakes import Clock, FakeComponent

MON_10AM = datetime.datetime(2026, 10, 12, 10, 0)


def make(**kw):
    clock = Clock(MON_10AM)
    inh, ka = FakeComponent(), FakeComponent()
    return Guard(Settings(**kw), inh, ka, clock=clock), inh, ka, clock


def test_arm_and_disarm():
    g, inh, ka, _ = make()
    assert g.status == "paused"
    assert g.arm() is True
    assert g.status == "active" and inh.running and ka.running
    assert g.status_text() == "Active"
    assert g.disarm() is True
    assert g.status == "paused" and not inh.running and not ka.running


def test_time_limit_expires():
    g, inh, _, clock = make(duration=30)
    g.arm()
    assert g.status_text() == "Active until 10:30"
    clock.now += datetime.timedelta(minutes=29)
    assert g.evaluate() is False
    clock.now += datetime.timedelta(minutes=1)
    assert g.evaluate() is True
    assert g.status == "paused" and not inh.running


def test_rearm_restarts_time_limit():
    g, _, _, clock = make(duration=60)
    g.arm()
    clock.now += datetime.timedelta(minutes=45)
    g.arm()
    assert g.expires_at == MON_10AM + datetime.timedelta(minutes=105)


def test_waits_outside_active_hours_then_engages():
    g, inh, _, clock = make(schedule_enabled=True, schedule_start="11:00", schedule_end="12:00")
    g.arm()
    assert g.status == "waiting" and not inh.running
    assert g.status_text() == "Waiting for active hours"
    clock.now = MON_10AM.replace(hour=11)
    assert g.evaluate() is True
    assert g.status == "active" and inh.running
    clock.now = MON_10AM.replace(hour=12)
    assert g.evaluate() is True
    assert g.status == "waiting" and not inh.running


def test_components_start_once():
    g, inh, ka, _ = make()
    g.arm()
    g.evaluate()
    g.arm()
    assert (inh.starts, ka.starts) == (1, 1)
