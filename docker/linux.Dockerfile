# Build environment for the Linux release (Ubuntu 24.04 ships Python 3.12).
FROM ubuntu:24.04
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-venv python3-dev build-essential pkg-config binutils \
      libgirepository-2.0-dev libcairo2-dev gir1.2-ayatanaappindicator3-0.1 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
