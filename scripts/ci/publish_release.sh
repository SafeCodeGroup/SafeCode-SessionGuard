#!/usr/bin/env bash
# Upload this platform's files to the tag's GitHub Release.
# The first platform to finish creates the release as a draft; the release is
# published once every platform's files are attached (the last uploader always
# sees the full set).
set -euo pipefail
TAG="$GITHUB_REF_NAME"
# macOS apple-silicon + intel (.dmg + .zip each) = 4, Windows x64/x86/arm64
# .zip = 3, Linux x86_64/aarch64/armv7l/i686 .tar.gz + .deb = 8,
# Linux x86_64/aarch64 .rpm = 2
EXPECTED=17
shopt -s nullglob
files=(dist/*.dmg dist/*.zip dist/*.tar.gz dist/*.deb dist/*.rpm)
[ ${#files[@]} -gt 0 ] || { echo "No release files in dist/" >&2; exit 1; }

if ! gh release view "$TAG" >/dev/null 2>&1; then
  sed "s/{version}/${TAG#v}/g" packaging/RELEASE_NOTES.md > /tmp/release-notes.md
  gh release create "$TAG" --draft --title "SafeCode SessionGuard ${TAG#v}" \
    --notes-file /tmp/release-notes.md --generate-notes \
    || gh release view "$TAG" >/dev/null  # another platform created it first
fi
gh release upload "$TAG" "${files[@]}" --clobber
count=$(gh release view "$TAG" --json assets --jq '.assets | length')
echo "Release $TAG has $count/$EXPECTED files"
if [ "$count" -ge "$EXPECTED" ]; then
  gh release edit "$TAG" --draft=false
  echo "Published $TAG"
fi
