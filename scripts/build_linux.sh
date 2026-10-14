#!/usr/bin/env bash
# Build dist/SafeCodeSessionGuard/ and a .tar.gz for distribution.
# Needs system packages first (Debian/Ubuntu):
#   sudo apt-get install libgirepository-2.0-dev libcairo2-dev pkg-config \
#       gir1.2-ayatanaappindicator3-0.1
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d .venv ] || "${PYTHON:-python3}" -m venv .venv
.venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pyinstaller --noconfirm --clean SafeCodeSessionGuard.spec

VERSION=$(.venv/bin/python -c 'import sessionguard; print(sessionguard.__version__)')
NAME="SafeCodeSessionGuard-$VERSION-linux-$(uname -m)"
cp packaging/linux/install.sh dist/SafeCodeSessionGuard/install.sh
cp assets/icon-256.png dist/SafeCodeSessionGuard/safecode-sessionguard.png
tar -czf "dist/$NAME.tar.gz" -C dist SafeCodeSessionGuard
echo "Built: dist/SafeCodeSessionGuard/, dist/$NAME.tar.gz"
