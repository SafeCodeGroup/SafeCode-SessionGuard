#!/usr/bin/env bash
# Build dist/SafeCodeSessionGuard/ and a .tar.gz for distribution.
# Needs system packages first (Debian/Ubuntu):
#   sudo apt-get install libgirepository-2.0-dev libcairo2-dev pkg-config \
#       gir1.2-ayatanaappindicator3-0.1 gir1.2-girepository-3.0
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d .venv ] || "${PYTHON:-python3}" -m venv .venv
.venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pyinstaller --noconfirm --clean SafeCodeSessionGuard.spec

# Without the GIRepository typelib PyInstaller silently leaves out GTK and
# AppIndicator support, and the app crashes at startup. Fail the build instead.
for typelib in AyatanaAppIndicator3-0.1 Gtk-3.0 DBus-1.0 GObject-2.0 GLib-2.0; do
  if ! find dist/SafeCodeSessionGuard -name "$typelib.typelib" | grep -q .; then
    echo "ERROR: $typelib.typelib missing from bundle (install gir1.2-girepository-3.0)" >&2
    exit 1
  fi
done

VERSION=$(.venv/bin/python -c 'import sessionguard; print(sessionguard.__version__)')
NAME="SafeCodeSessionGuard-$VERSION-linux-$(uname -m)"
cp packaging/linux/install.sh dist/SafeCodeSessionGuard/install.sh
cp assets/icon-256.png dist/SafeCodeSessionGuard/safecode-sessionguard.png
tar -czf "dist/$NAME.tar.gz" -C dist SafeCodeSessionGuard
echo "Built: dist/SafeCodeSessionGuard/, dist/$NAME.tar.gz"
