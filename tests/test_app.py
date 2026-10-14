import pytest

from sessionguard.app import SessionGuardApp, duration_label
from sessionguard.icon import create_icon_image
from sessionguard.settings import Settings, load, save
from tests.fakes import FakeComponent


class FakeAutostart:
    def __init__(self):
        self.enabled = False

    def is_enabled(self):
        return self.enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


@pytest.fixture
def app(tmp_path):
    return SessionGuardApp(
        settings_path=tmp_path / "settings.json",
        inhibitor=FakeComponent(),
        keepalive=FakeComponent(),
        autostart=FakeAutostart(),
    )


def labels(menu):
    return [item.text for item in menu.items if item.text]


def find(menu, text):
    return next(item for item in menu.items if item.text == text)


@pytest.mark.parametrize(
    "status,pixel",
    [
        ("active", (46, 204, 113, 255)),
        ("waiting", (243, 156, 18, 255)),
        ("paused", (149, 165, 166, 255)),
    ],
)
def test_icon_colors(status, pixel):
    img = create_icon_image(status)
    assert img.size == (64, 64) and img.mode == "RGBA"
    assert img.getpixel((12, 32)) == pixel
    assert img.getpixel((0, 0))[3] == 0


def test_duration_labels():
    assert [duration_label(m) for m in (0, 30, 60, 120)] == [
        "No time limit",
        "30 minutes",
        "1 hour",
        "2 hours",
    ]


def test_menu_structure(app):
    menu = app._build_menu()
    texts = labels(menu)
    assert texts[0] == "▶ Start Guard"
    assert texts[1] == "Paused"
    for expected in (
        "Keep awake for",
        "Method",
        "Interval",
        "Only when idle",
        "Launch at login",
        "Edit settings…",
        "Reload settings",
        "Visit safecodeg.com",
        "Quit",
    ):
        assert expected in texts
    assert "Active hours (09:00–18:00, Mon–Fri)" in texts
    assert any(t.startswith("SafeCode SessionGuard 1.") for t in texts)


def test_permission_item_only_when_input_blocked(app, monkeypatch):
    import sessionguard.app as appmod

    item = find(app._build_menu(), "⚠ Allow input in Accessibility settings…")
    monkeypatch.setattr(appmod, "input_allowed", lambda: True)
    assert not item.visible
    monkeypatch.setattr(appmod, "input_allowed", lambda: False)
    assert item.visible
    app.settings.method = "none"
    assert not item.visible


def test_toggle_starts_and_stops(app):
    app._toggle()
    assert app.guard.status == "active" and app.keepalive.running
    assert labels(app._build_menu())[0] == "⏸ Stop Guard"
    app._toggle()
    assert app.guard.status == "paused" and not app.keepalive.running


def test_menu_choices_are_saved(app):
    menu = app._build_menu()
    method = find(menu, "Method").submenu
    find(method, "Prevent sleep only")(None)
    find(find(menu, "Interval").submenu, "300 seconds")(None)
    find(menu, "Only when idle")(None)
    saved = load(app.settings_path)
    assert (saved.method, saved.interval, saved.idle_only) == ("none", 300, False)
    assert find(method, "Prevent sleep only").checked


def test_choosing_duration_restarts_timer(app):
    app._toggle()
    menu = app._build_menu()
    find(find(menu, "Keep awake for").submenu, "1 hour")(None)
    assert app.guard.expires_at is not None
    assert app.guard.status_text().startswith("Active until ")


def test_active_hours_toggle_reevaluates(app):
    app.settings.schedule_start, app.settings.schedule_end = "00:00", "00:00"
    app.settings.schedule_days = []
    app._toggle()
    find(app._build_menu(), "Active hours (00:00–00:00, no days)")(None)
    assert app.guard.status == "waiting"


def test_launch_at_login_toggle(app):
    item = find(app._build_menu(), "Launch at login")
    item(None)
    assert app.autostart.enabled and item.checked
    item(None)
    assert not app.autostart.enabled


def test_reload_picks_up_file_edits(app):
    save(Settings(interval=120, method="key"), app.settings_path)
    keep = app.settings
    app._reload_settings()
    assert keep is app.settings and app.settings.interval == 120 and app.settings.method == "key"
