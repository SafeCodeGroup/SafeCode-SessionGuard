#!/usr/bin/env bash
# Build "dist/SafeCode SessionGuard.app" plus a .zip and .dmg for distribution.
set -euo pipefail
cd "$(dirname "$0")/.."

[ -d .venv ] || "${PYTHON:-python3.12}" -m venv .venv
.venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pyinstaller --noconfirm --clean SafeCodeSessionGuard.spec

VERSION=$(.venv/bin/python -c 'import sessionguard; print(sessionguard.__version__)')
APP="dist/SafeCode SessionGuard.app"
NAME="SafeCodeSessionGuard-$VERSION-macos-$(uname -m)"
rm -f "dist/$NAME.zip"
ditto -c -k --keepParent "$APP" "dist/$NAME.zip"
echo "Built: $APP, dist/$NAME.zip"
if scripts/make_dmg.sh "$APP" "dist/$NAME.dmg"; then
  echo "Built: dist/$NAME.dmg"
elif [ -n "${CI:-}" ]; then
  exit 1
else
  echo "WARNING: DMG step failed (disk image creation not permitted here?)" >&2
fi
