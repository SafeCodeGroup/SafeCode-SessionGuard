#!/usr/bin/env bash
# Runs inside a distro container: install the .deb (apt) or .rpm (dnf) from
# dist/, self-test and launch it, then uninstall and check it is gone.
set -euxo pipefail
ARCH="${ARCH:-$(uname -m)}"
if command -v apt-get >/dev/null; then
  case "$ARCH" in x86_64) A=amd64 ;; aarch64) A=arm64 ;; armv7l) A=armhf ;; i686) A=i386 ;; esac
  apt-get install -y ./dist/safecode-sessionguard_*_"$A".deb >/dev/null
  remove() { apt-get remove -y safecode-sessionguard >/dev/null; }
else
  dnf install -y ./dist/safecode-sessionguard-*."$ARCH".rpm >/dev/null
  remove() { dnf remove -y safecode-sessionguard >/dev/null; }
fi
test -x /usr/bin/safecode-sessionguard
test -f /usr/share/applications/safecode-sessionguard.desktop
T=$(mktemp -d)
if ! dbus-run-session -- xvfb-run -a safecode-sessionguard --self-test "$T/selftest.txt"; then
  cat "$T/selftest.txt"
  exit 1
fi
cat "$T/selftest.txt"
dbus-run-session -- xvfb-run -a python3 scripts/smoke_test.py /usr/bin/safecode-sessionguard
remove
test ! -e /opt/safecode-sessionguard && test ! -e /usr/bin/safecode-sessionguard
