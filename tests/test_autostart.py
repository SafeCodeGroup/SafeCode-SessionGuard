import plistlib

from sessionguard.autostart import RUN_KEY, Autostart

CMD = ["/Applications/SafeCode SessionGuard.app/Contents/MacOS/SafeCodeSessionGuard"]


def test_mac_launch_agent(tmp_path):
    a = Autostart("Darwin", home=tmp_path, command=CMD)
    assert not a.is_enabled()
    a.enable()
    assert a.is_enabled()
    plist = plistlib.loads(a.path.read_bytes())
    assert plist["ProgramArguments"] == CMD and plist["RunAtLoad"] is True
    assert a.path == tmp_path / "Library/LaunchAgents/com.safecodeg.sessionguard.plist"
    a.disable()
    assert not a.is_enabled()
    a.disable()  # idempotent


def test_linux_desktop_entry(tmp_path):
    a = Autostart("Linux", home=tmp_path, env={}, command=["/opt/Session Guard/SessionGuard"])
    a.enable()
    text = a.path.read_text()
    assert a.path == tmp_path / ".config/autostart/safecode-sessionguard.desktop"
    assert "Exec='/opt/Session Guard/SessionGuard'" in text
    assert "Name=SafeCode SessionGuard" in text
    a.disable()
    assert not a.is_enabled()


class FakeWinreg:
    HKEY_CURRENT_USER = "HKCU"
    KEY_SET_VALUE = 2
    REG_SZ = 1

    def __init__(self):
        self.values = {}

    class _Key:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def CreateKey(self, root, path):
        return self._Key(path)

    def OpenKey(self, root, path, *args):
        return self._Key(path)

    def SetValueEx(self, key, name, reserved, kind, value):
        self.values[(key.path, name)] = value

    def QueryValueEx(self, key, name):
        try:
            return self.values[(key.path, name)], self.REG_SZ
        except KeyError:
            raise FileNotFoundError(name) from None

    def DeleteValue(self, key, name):
        try:
            del self.values[(key.path, name)]
        except KeyError:
            raise FileNotFoundError(name) from None


def test_windows_run_key():
    reg = FakeWinreg()
    a = Autostart("Windows", command=[r"C:\Program Files\SessionGuard\SessionGuard.exe"], winreg=reg)
    assert not a.is_enabled()
    a.enable()
    expected = r'"C:\Program Files\SessionGuard\SessionGuard.exe"'
    assert reg.values[(RUN_KEY, "SafeCodeSessionGuard")] == expected
    assert a.is_enabled()
    a.disable()
    assert not a.is_enabled()
    a.disable()
