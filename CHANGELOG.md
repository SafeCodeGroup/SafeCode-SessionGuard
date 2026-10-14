# Changelog

## 1.2.0

- New downloads:
  - Windows 32-bit (x86)
  - Raspberry Pi OS 32-bit (armv7l / armhf)
  - Linux 32-bit PC (i686 / i386)
- Native Linux packages: `.deb` for Ubuntu / Debian / Mint / Raspberry Pi OS (amd64, arm64,
  armhf, i386) and `.rpm` for Fedora / RHEL / openSUSE (x86_64, aarch64).
- 64-bit Linux builds now need only glibc 2.35, so they also run on Ubuntu 22.04 and Debian 12.
- macOS downloads are named for the hardware: `macos-apple-silicon` (M1–M5) and `macos-intel`.
- Release notes include a "which download do I need" table.

## 1.1.1

- Native binaries for every supported OS and CPU:
  - macOS Apple Silicon and Intel
  - Windows x64 and ARM64
  - Linux x86_64 and aarch64
- Linux: bundle every GObject typelib the tray needs, so it also runs on Debian, Fedora and Arch
  without extra `gir1.2-*` packages.
- Fatal startup errors are logged and the app exits instead of hanging.
- Clear error when no desktop D-Bus session is available on Linux.
- `--self-test` mode to check a build; CI runs it on every target.
- Windows: the sleep block is reliably released, the mouse nudge counts as user activity, and the
  menu refreshes safely.

## 1.1.0

- Renamed to **SafeCode SessionGuard** (bundle ID `com.safecodeg.sessionguard`).
- Key-press method (F15; Shift on macOS) and a "prevent sleep only" mode.
- "Only when idle" nudging, using the OS idle time.
- Keep-awake time limits (30 min – 4 h) and active hours, including overnight ranges.
- Launch at login on macOS, Windows and Linux.
- Persistent, validated JSON settings with Edit / Reload from the menu.
- Single-instance lock, rotating log file and crash logging.
- macOS Accessibility-permission prompt.
- Linux sleep inhibitor no longer outlives a crashed app.
- App icon, DMG installer, and CI that builds, smoke-tests and releases for macOS, Windows
  and Linux.

## 1.0.0

- Tray app with sleep prevention (macOS / Windows / Linux) and a periodic mouse jiggle.
