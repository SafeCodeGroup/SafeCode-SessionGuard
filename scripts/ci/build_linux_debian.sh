#!/usr/bin/env bash
# Build, test and package a 32-bit Linux release inside Debian 12 (glibc 2.36,
# the base of Raspberry Pi OS Bookworm). PyPI has no 32-bit wheels for PyGObject
# or Pillow, so Debian's own python3-gi / python3-pil are used.
# Usage: scripts/ci/build_linux_debian.sh <docker-platform> <arch-name>
#   e.g. linux/arm/v7 armv7l   |   linux/386 i686
set -euo pipefail
cd "$(dirname "$0")/../.."
PLATFORM="$1"
ARCH="$2"
mkdir -p dist
docker run --rm --platform "$PLATFORM" -e ARCH="$ARCH" \
  -v "$PWD:/src:ro" -v "$PWD/dist:/out" debian:bookworm bash -c '
    set -euxo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq --no-install-recommends \
      python3 python3-venv python3-dev python3-gi python3-pil build-essential zlib1g-dev \
      gir1.2-ayatanaappindicator3-0.1 gir1.2-girepository-2.0 libayatana-appindicator3-1 \
      xvfb xauth dbus procps file binutils ca-certificates >/dev/null
    mkdir /work && cd /work
    tar -C /src --exclude=.venv --exclude=build --exclude=dist --exclude=dist-docker --exclude=.git -cf - . | tar -xf -
    python3 -m venv --system-site-packages /venv
    /venv/bin/pip install -q pystray==0.19.5 pynput==1.8.2 pyinstaller==6.22.3 pytest
    /venv/bin/python -m pytest -q -p no:cacheprovider
    VENV=/venv REQUIREMENTS= NO_RPM=1 scripts/build_linux.sh
    file dist/SafeCodeSessionGuard/SafeCodeSessionGuard
    HOME=$(mktemp -d) scripts/ci/linux_install_test.sh
    scripts/ci/package_install_test.sh
    cp dist/*.tar.gz dist/*.deb /out/
  '
ls -l dist/*-linux-"$ARCH".tar.gz dist/*.deb
