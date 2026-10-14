#!/usr/bin/env bash
# Upload this platform's files to the tag's GitHub Release.
# The first platform to finish creates the release as a draft; the release is
# published once every platform's files are attached (the last uploader always
# sees the full set).
set -euo pipefail
TAG="$GITHUB_REF_NAME"
EXPECTED=4  # macOS .dmg + .zip, Windows .zip, Linux .tar.gz
shopt -s nullglob
files=(dist/*.dmg dist/*.zip dist/*.tar.gz)
[ ${#files[@]} -gt 0 ] || { echo "No release files in dist/" >&2; exit 1; }

if ! gh release view "$TAG" >/dev/null 2>&1; then
  gh release create "$TAG" --draft --title "SafeCode SessionGuard ${TAG#v}" --generate-notes \
    || gh release view "$TAG" >/dev/null  # another platform created it first
fi
gh release upload "$TAG" "${files[@]}" --clobber
count=$(gh release view "$TAG" --json assets --jq '.assets | length')
echo "Release $TAG has $count/$EXPECTED files"
if [ "$count" -ge "$EXPECTED" ]; then
  gh release edit "$TAG" --draft=false
  echo "Published $TAG"
fi
