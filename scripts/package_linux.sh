#!/usr/bin/env bash
# Wrap the PyInstaller bundle in dist/SafeCodeSessionGuard into native packages:
#   dist/safecode-sessionguard_<ver>_<debarch>.deb   (Ubuntu, Debian, Mint, Raspberry Pi OS)
#   dist/safecode-sessionguard-<ver>-1.<arch>.rpm    (Fedora, RHEL/Rocky/Alma, openSUSE)
# Usage: scripts/package_linux.sh <version> <arch>     (arch as in `uname -m`)
# Set NO_RPM=1 to skip the .rpm (it needs rpmbuild).
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION="$1"
ARCH="$2"
PKG=safecode-sessionguard
case "$ARCH" in
  x86_64) DEBARCH=amd64 ;;
  aarch64) DEBARCH=arm64 ;;
  armv7l) DEBARCH=armhf ;;
  i686) DEBARCH=i386 ;;
  *) echo "Unsupported arch $ARCH" >&2; exit 1 ;;
esac

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
ROOT="$STAGE/root"
mkdir -p "$ROOT/opt" "$ROOT/usr/bin" "$ROOT/usr/share/applications" \
  "$ROOT/usr/share/icons/hicolor/256x256/apps"
cp -a dist/SafeCodeSessionGuard "$ROOT/opt/$PKG"
rm -f "$ROOT/opt/$PKG/install.sh"  # the package manager handles install/uninstall
ln -s "/opt/$PKG/SafeCodeSessionGuard" "$ROOT/usr/bin/$PKG"
cp assets/icon-256.png "$ROOT/usr/share/icons/hicolor/256x256/apps/$PKG.png"
cat > "$ROOT/usr/share/applications/$PKG.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=SafeCode SessionGuard
Comment=Keep your computer awake and your session active
Exec=/opt/$PKG/SafeCodeSessionGuard
Icon=$PKG
Categories=Utility;
Terminal=false
DESKTOP
SUMMARY="Keep your computer awake and your session active"
DESCRIPTION="SafeCode SessionGuard prevents sleep, screen lock and idle status from the system tray."

# --- .deb
mkdir -p "$ROOT/DEBIAN"
cat > "$ROOT/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $VERSION
Architecture: $DEBARCH
Maintainer: SafeCode Group <https://www.safecodeg.com/>
Homepage: https://www.safecodeg.com/
Section: utils
Priority: optional
Depends: libayatana-appindicator3-1
Recommends: xprintidle
Installed-Size: $(du -sk "$ROOT/opt" | cut -f1)
Description: $SUMMARY
 $DESCRIPTION
CONTROL
DEB="dist/${PKG}_${VERSION}_${DEBARCH}.deb"
dpkg-deb --build --root-owner-group -Zxz "$ROOT" "$DEB" >/dev/null
rm -rf "$ROOT/DEBIAN"
echo "Built: $DEB"

# --- .rpm (64-bit only; 32-bit RPM distros are effectively gone)
if [ -n "${NO_RPM:-}" ] || [ "$DEBARCH" = armhf ] || [ "$DEBARCH" = i386 ]; then
  exit 0
fi
TOP="$STAGE/rpm"
mkdir -p "$TOP"/{BUILD,RPMS,SPECS,SOURCES,SRPMS}
cat > "$TOP/SPECS/$PKG.spec" <<SPEC
# The payload is a prebuilt PyInstaller bundle: don't strip it (that would
# remove the embedded archive) or derive dependencies from its private libraries.
%global __os_install_post %{nil}
%global debug_package %{nil}
%define _build_id_links none
AutoReqProv: no
Name: $PKG
Version: $VERSION
Release: 1
Summary: $SUMMARY
License: Proprietary
URL: https://www.safecodeg.com/
Requires: libayatana-appindicator-gtk3

%description
$DESCRIPTION

%install
mkdir -p %{buildroot}
cp -a $ROOT/. %{buildroot}/

%files
/opt/$PKG
/usr/bin/$PKG
/usr/share/applications/$PKG.desktop
/usr/share/icons/hicolor/256x256/apps/$PKG.png
SPEC
rpmbuild --quiet --define "_topdir $TOP" --target "$ARCH" -bb "$TOP/SPECS/$PKG.spec"
cp "$TOP"/RPMS/*/*.rpm dist/
echo "Built: $(ls dist/*.rpm)"
