#!/usr/bin/env bash
# Build the Linux release from any OS with Docker (macOS, Windows/WSL, Linux).
# Usage: scripts/build_linux_docker.sh [amd64|arm64]   (default: amd64)
# Output: dist/SafeCodeSessionGuard-<ver>-linux-<arch>.tar.gz
set -euo pipefail
cd "$(dirname "$0")/.."
ARCH="${1:-amd64}"
IMAGE="safecode-sessionguard-build:linux-$ARCH"

docker build --platform "linux/$ARCH" -t "$IMAGE" -f docker/linux.Dockerfile docker
mkdir -p dist
# Copy the source into the container (minus host venv/build output) so the
# host's .venv and dist/ are never touched by the Linux build.
docker run --rm --platform "linux/$ARCH" \
  -v "$PWD:/src:ro" -v "$PWD/dist:/out" "$IMAGE" bash -c '
    set -euo pipefail
    tar -C /src --exclude=.venv --exclude=build --exclude=dist --exclude=.git -cf - . | tar -xf -
    PYTHON=python3 scripts/build_linux.sh
    cp dist/*.tar.gz /out/
  '
ls -1 dist/*linux*.tar.gz
