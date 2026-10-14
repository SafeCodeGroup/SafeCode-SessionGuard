#!/usr/bin/env bash
# Runs inside a distro container: install the Linux download, launch it, uninstall.
set -euxo pipefail
T=$(mktemp -d)
tar -xzf dist/SafeCodeSessionGuard-*-linux-x86_64.tar.gz -C "$T"
"$T/SafeCodeSessionGuard/install.sh"
if ! xvfb-run -a dbus-launch --exit-with-session \
    python3 scripts/smoke_test.py "$HOME/.local/bin/safecode-sessionguard"; then
  cat ~/.config/SafeCodeSessionGuard/logs/*.log 2>/dev/null || true
  exit 1
fi
"$T/SafeCodeSessionGuard/install.sh" --uninstall
test ! -e "$HOME/.local/opt/SafeCodeSessionGuard"
