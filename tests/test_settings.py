import json
from pathlib import Path

from sessionguard.settings import Settings, config_dir, load, save


def test_defaults():
    s = Settings()
    assert (s.method, s.interval, s.idle_only, s.duration) == ("mouse", 60, True, 0)
    assert s.schedule_days == [0, 1, 2, 3, 4]


def test_round_trip(tmp_path):
    path = tmp_path / "nested" / "settings.json"
    s = Settings(method="key", interval=120, schedule_enabled=True, schedule_days=[5, 6])
    save(s, path)
    assert load(path) == s
    assert not path.with_name("settings.json.tmp").exists()


def test_invalid_values_fall_back_to_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "method": "teleport",
                "interval": True,
                "duration": -5,
                "schedule_start": "25:99",
                "schedule_days": [1, 9],
                "unknown": 1,
                "idle_only": False,
            }
        )
    )
    s = load(path)
    d = Settings()
    assert (s.method, s.interval, s.duration, s.schedule_start, s.schedule_days) == (
        d.method,
        d.interval,
        d.duration,
        d.schedule_start,
        d.schedule_days,
    )
    assert s.idle_only is False


def test_corrupt_or_missing_file_gives_defaults(tmp_path):
    bad = tmp_path / "settings.json"
    bad.write_text("{not json")
    assert load(bad) == Settings()
    assert load(tmp_path / "missing.json") == Settings()


def test_update_from_mutates_in_place():
    s = Settings()
    ref = s
    s.update_from(Settings(interval=300))
    assert ref.interval == 300


def test_config_dir_per_platform():
    home = Path("/home/u")
    assert config_dir("Darwin", {}, home) == home / "Library/Application Support/SafeCodeSessionGuard"
    assert config_dir("Windows", {"APPDATA": "C:/AppData"}, home) == Path("C:/AppData/SafeCodeSessionGuard")
    assert config_dir("Linux", {}, home) == home / ".config/SafeCodeSessionGuard"
    assert config_dir("Linux", {"XDG_CONFIG_HOME": "/x"}, home) == Path("/x/SafeCodeSessionGuard")
