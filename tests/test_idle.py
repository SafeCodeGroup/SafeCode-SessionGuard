import subprocess
from unittest import mock

import pytest

from sessionguard import idle


def test_linux_parses_xprintidle_millis():
    result = mock.Mock(stdout="12345\n")
    with mock.patch.object(subprocess, "run", return_value=result):
        assert idle.idle_seconds("Linux") == pytest.approx(12.345)


def test_linux_without_xprintidle_is_unknown():
    with mock.patch.object(subprocess, "run", side_effect=FileNotFoundError):
        assert idle.idle_seconds("Linux") is None


def test_unknown_platform_is_unknown():
    assert idle.idle_seconds("Plan9") is None


@pytest.mark.skipif(idle.SYSTEM not in ("Darwin", "Windows"), reason="needs native idle API")
def test_native_idle_returns_seconds():
    value = idle.idle_seconds()
    assert isinstance(value, float) and value >= 0
