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
# hdiutil sometimes fails with "Resource busy" on CI machines; retry.
for attempt in 1 2 3; do
  if hdiutil create -volname "SafeCode SessionGuard" -srcfolder "$STAGE" -format UDZO -ov "$OUT"; then
    exit 0
  fi
  echo "hdiutil attempt $attempt failed" >&2
  sleep 5
done
exit 1
