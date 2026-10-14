# Changelog

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
