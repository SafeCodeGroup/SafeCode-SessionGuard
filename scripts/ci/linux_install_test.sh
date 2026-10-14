#!/usr/bin/env bash
# Runs inside a distro container: install the Linux download, launch it, uninstall.
set -euxo pipefail
T=$(mktemp -d)
tar -xzf dist/SafeCodeSessionGuard-*-linux-"${ARCH:-$(uname -m)}".tar.gz -C "$T"
"$T/SafeCodeSessionGuard/install.sh"
if ! dbus-run-session -- xvfb-run -a \
    "$HOME/.local/bin/safecode-sessionguard" --self-test "$T/selftest.txt"; then
  cat "$T/selftest.txt"
  exit 1
fi
cat "$T/selftest.txt"
if ! dbus-run-session -- xvfb-run -a \
    python3 scripts/smoke_test.py "$HOME/.local/bin/safecode-sessionguard"; then
  cat ~/.config/SafeCodeSessionGuard/logs/*.log 2>/dev/null || true
  exit 1
fi
"$T/SafeCodeSessionGuard/install.sh" --uninstall
test ! -e "$HOME/.local/opt/SafeCodeSessionGuard"
