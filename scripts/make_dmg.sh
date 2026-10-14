#!/usr/bin/env bash
# Usage: make_dmg.sh <path/to/App.app> <out.dmg>
# Creates a compressed drag-to-Applications disk image.
set -euo pipefail
APP="$1"
OUT="$2"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "$OUT"
hdiutil create -volname "SafeCode SessionGuard" -srcfolder "$STAGE" -format UDZO -ov "$OUT"
