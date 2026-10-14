"""Decides when sleep prevention and input nudges should be running."""

import datetime
import logging
import threading

from .schedule import in_schedule, parse_hhmm

log = logging.getLogger(__name__)


class Guard:
    """Ties the user's on/off choice, time limit and active hours together.

    armed   - the user turned the guard on
    engaged - inhibitor and keep-alive are actually running
    """

    def __init__(self, settings, inhibitor, keepalive, clock=datetime.datetime.now):
        self.settings = settings
        self.inhibitor = inhibitor
        self.keepalive = keepalive
        self._clock = clock
        self._lock = threading.RLock()
        self.armed = False
        self.engaged = False
        self.expires_at = None

    @property
    def status(self) -> str:
        if self.engaged:
            return "active"
        return "waiting" if self.armed else "paused"

    def status_text(self) -> str:
        status = self.status
        if status == "active":
            if self.expires_at:
                return f"Active until {self.expires_at:%H:%M}"
            return "Active"
        if status == "waiting":
            return "Waiting for active hours"
        return "Paused"

    def arm(self) -> bool:
        """Turn on (or restart the time limit). Returns True if status changed."""
        with self._lock:
            before = self.status
            minutes = self.settings.duration
            self.armed = True
            self.expires_at = self._clock() + datetime.timedelta(minutes=minutes) if minutes else None
            return self._apply(before)

    def disarm(self) -> bool:
        with self._lock:
            before = self.status
            self.armed = False
            self.expires_at = None
            return self._apply(before)

    def evaluate(self) -> bool:
        """Re-check time limit and active hours. Returns True if status changed."""
        with self._lock:
            return self._apply(self.status)

    def in_hours(self, now) -> bool:
        s = self.settings
        if not s.schedule_enabled:
            return True
        return in_schedule(now, parse_hhmm(s.schedule_start), parse_hhmm(s.schedule_end), s.schedule_days)

    def _apply(self, before: str) -> bool:
        now = self._clock()
        if self.armed and self.expires_at and now >= self.expires_at:
            self.armed = False
            self.expires_at = None
        want = self.armed and self.in_hours(now)
        if want and not self.engaged:
            self.inhibitor.start()
            self.keepalive.start()
            self.engaged = True
            log.info("Engaged")
        elif not want and self.engaged:
            self.keepalive.stop()
            self.inhibitor.stop()
            self.engaged = False
            log.info("Disengaged (%s)", self.status)
        return self.status != before
