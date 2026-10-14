"""User settings, persisted as JSON in the per-user config directory."""

import json
import os
import platform
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from . import APP_ID
from .schedule import parse_hhmm

METHODS = ("mouse", "key", "none")
INTERVALS = (30, 60, 120, 300)  # seconds
DURATIONS = (0, 30, 60, 120, 240)  # minutes; 0 = no time limit


def config_dir(system=None, env=None, home=None) -> Path:
    system = system or platform.system()
    env = os.environ if env is None else env
    home = Path(home) if home else Path.home()
    if system == "Darwin":
        return home / "Library" / "Application Support" / APP_ID
    if system == "Windows":
        return Path(env.get("APPDATA") or home / "AppData" / "Roaming") / APP_ID
    return Path(env.get("XDG_CONFIG_HOME") or home / ".config") / APP_ID


def default_settings_path() -> Path:
    return config_dir() / "settings.json"


@dataclass
class Settings:
    method: str = "mouse"
    interval: int = 60
    idle_only: bool = True
    duration: int = 0
    schedule_enabled: bool = False
    schedule_start: str = "09:00"
    schedule_end: str = "18:00"
    schedule_days: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    start_on_launch: bool = True

    @classmethod
    def from_dict(cls, data) -> "Settings":
        """Build settings, keeping defaults for missing or invalid values."""
        settings = cls()
        if not isinstance(data, dict):
            return settings
        for name, valid in _CHECKS.items():
            if name in data and valid(data[name]):
                setattr(settings, name, data[name])
        return settings

    def to_dict(self) -> dict:
        return asdict(self)

    def update_from(self, other: "Settings") -> None:
        """Copy values in place so components holding this object see them."""
        for f in fields(self):
            setattr(self, f.name, getattr(other, f.name))


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_hhmm(v) -> bool:
    try:
        parse_hhmm(v)
        return True
    except (TypeError, ValueError):
        return False


_CHECKS = {
    "method": lambda v: v in METHODS,
    "interval": lambda v: _is_int(v) and v >= 5,
    "idle_only": lambda v: isinstance(v, bool),
    "duration": lambda v: _is_int(v) and v >= 0,
    "schedule_enabled": lambda v: isinstance(v, bool),
    "schedule_start": _is_hhmm,
    "schedule_end": _is_hhmm,
    "schedule_days": lambda v: isinstance(v, list) and all(_is_int(d) and 0 <= d <= 6 for d in v),
    "start_on_launch": lambda v: isinstance(v, bool),
}


def load(path: Path) -> Settings:
    try:
        return Settings.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return Settings()


def save(settings: Settings, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(settings.to_dict(), indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)
