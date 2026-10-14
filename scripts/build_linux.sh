#!/usr/bin/env bash
# Build dist/SafeCodeSessionGuard/ and a .tar.gz for distribution.
# Needs system packages first (Debian/Ubuntu):
#   sudo apt-get install libgirepository1.0-dev libcairo2-dev pkg-config \
#       gir1.2-ayatanaappindicator3-0.1 gir1.2-girepository-2.0
# Env overrides: VENV (default .venv), REQUIREMENTS (default requirements-dev.txt,
# empty = skip pip), ARCH (default: uname -m).
set -euo pipefail
cd "$(dirname "$0")/.."

VENV="${VENV:-.venv}"
REQUIREMENTS="${REQUIREMENTS-requirements-dev.txt}"
[ -d "$VENV" ] || "${PYTHON:-python3}" -m venv "$VENV"
[ -z "$REQUIREMENTS" ] || "$VENV/bin/pip" install -q -r "$REQUIREMENTS"
"$VENV/bin/pyinstaller" --noconfirm --clean SafeCodeSessionGuard.spec

# Without the GIRepository typelib PyInstaller silently leaves out GTK and
# AppIndicator support, and the app crashes at startup. Fail the build instead.
for typelib in AyatanaAppIndicator3-0.1 Gtk-3.0 DBus-1.0 GObject-2.0 GLib-2.0; do
  if ! find dist/SafeCodeSessionGuard -name "$typelib.typelib" | grep -q .; then
    echo "ERROR: $typelib.typelib missing from bundle (install gir1.2-girepository-2.0)" >&2
    exit 1
  fi
done

VERSION=$("$VENV/bin/python" -c 'import sessionguard; print(sessionguard.__version__)')
NAME="SafeCodeSessionGuard-$VERSION-linux-${ARCH:-$(uname -m)}"
cp packaging/linux/install.sh dist/SafeCodeSessionGuard/install.sh
cp assets/icon-256.png dist/SafeCodeSessionGuard/safecode-sessionguard.png
tar -czf "dist/$NAME.tar.gz" -C dist SafeCodeSessionGuard
echo "Built: dist/SafeCodeSessionGuard/, dist/$NAME.tar.gz"
if command -v dpkg-deb >/dev/null; then
  command -v rpmbuild >/dev/null || NO_RPM=1
  NO_RPM="${NO_RPM:-}" scripts/package_linux.sh "$VERSION" "${ARCH:-$(uname -m)}"
else
  echo "WARNING: dpkg-deb not found; skipping .deb/.rpm packages" >&2
fi
