#!/usr/bin/env bash
# Runs inside a container: follow the README "Run from source" steps for Linux
# with the distro's own Python and PyGObject, run the tests, launch the app.
set -euxo pipefail
export PYTHONDONTWRITEBYTECODE=1
python3 --version
python3 -m venv --system-site-packages /tmp/venv
/tmp/venv/bin/pip install -q pystray==0.19.5 pynput==1.8.2 Pillow pytest
/tmp/venv/bin/python -m pytest -q -p no:cacheprovider
if ! dbus-run-session -- xvfb-run -a \
    /tmp/venv/bin/python scripts/smoke_test.py /tmp/venv/bin/python session_guard.py; then
  cat ~/.config/SafeCodeSessionGuard/logs/*.log 2>/dev/null || true
  exit 1
fi
