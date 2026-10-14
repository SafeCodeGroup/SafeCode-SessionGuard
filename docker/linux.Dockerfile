# Build environment for the Linux release. Ubuntu 22.04 (glibc 2.35) keeps the
# binary compatible with Ubuntu 22.04+, Debian 12+ and other 2022+ distros.
FROM ubuntu:22.04
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-venv python3-dev build-essential pkg-config binutils \
      libgirepository1.0-dev libcairo2-dev gir1.2-ayatanaappindicator3-0.1 \
      gir1.2-girepository-2.0 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
