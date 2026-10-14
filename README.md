# SafeCode SessionGuard

**Keep your computer awake and your session active — from the menu bar or system tray.**
A product of [SafeCode Group](https://www.safecodeg.com/).

SafeCode SessionGuard stops your computer from sleeping, locking the screen or showing you as
"away" while you're reading, presenting, running long jobs or watching a remote session. It runs
on **macOS, Windows and Linux**.

## Features

- **Sleep prevention** using each OS's own API, so the system knows why it is being kept awake.
- **Stay active:** a 1-pixel mouse move (moved straight back, so you never see it) or a harmless
  key press (F15; Shift on macOS) every 30 s – 5 min.
- **Only when idle:** nudges only start once you've stepped away, so they never get in the way
  while you're working.
- **Time limit:** keep awake for 30 min, 1, 2 or 4 hours, or with no limit.
- **Active hours:** for example 09:00–18:00, Mon–Fri. Overnight ranges like 22:00–06:00 work too.
- **Launch at login**, **saved settings**, and a status icon: green = active, amber = waiting for
  active hours, gray = paused.
- **Reliable:**
  - Only one copy can run at a time.
  - Any OS helper process stops automatically if the app crashes.
  - Uncaught errors go to a log file.

## Install

Download the file for your OS from the
[Releases page](https://github.com/SafeCodeGroup/SafeCode-SessionGuard/releases).

| OS | File | Install |
|---|---|---|
| macOS 11+ (Apple Silicon) | `SafeCodeSessionGuard-<ver>-macos-arm64.dmg` | Open and drag **SafeCode SessionGuard** to Applications |
| Windows 10/11 (x64) | `SafeCodeSessionGuard-<ver>-windows-x64.zip` | Unzip anywhere and run `SafeCodeSessionGuard.exe` |
| Linux x86_64 (X11) | `SafeCodeSessionGuard-<ver>-linux-x86_64.tar.gz` | `tar xzf …` and run `SafeCodeSessionGuard/SafeCodeSessionGuard` |

**First run**

- **macOS:** builds are not notarized yet. Right-click the app → **Open** the first time, or run
  `xattr -dr com.apple.quarantine "/Applications/SafeCode SessionGuard.app"`. To use the mouse or
  key nudge, allow the app in **System Settings → Privacy & Security → Accessibility**. The menu
  shows a ⚠ shortcut until you do. Sleep prevention works without this permission.
- **Windows:** builds are not code-signed yet. In the SmartScreen warning, choose
  **More info → Run anyway**.
- **Linux:** needs an AppIndicator-capable tray (GNOME with the AppIndicator extension, KDE, XFCE,
  …) and `libayatana-appindicator3`. Idle detection uses `xprintidle` if it's installed. On
  Wayland, the "only when idle" check falls back to a plain timer.

## Using it

Click the tray / menu-bar icon:

| Menu item | What it does |
|---|---|
| ▶ Start Guard / ⏸ Stop Guard | Turn the guard on or off. It starts automatically on launch. |
| Keep awake for | No time limit · 30 minutes · 1 / 2 / 4 hours |
| Method | Mouse jiggle · Key press · Prevent sleep only |
| Interval | 30 / 60 / 120 / 300 seconds between nudges |
| Only when idle | Nudge only after you've been inactive for one interval |
| Active hours | Run only inside the configured window |
| Launch at login | Start automatically when you sign in |
| Edit settings… / Reload settings | Open the settings file and apply your changes |

### Settings file

| OS | Settings | Log |
|---|---|---|
| macOS | `~/Library/Application Support/SafeCodeSessionGuard/settings.json` | `~/Library/Logs/SafeCodeSessionGuard/sessionguard.log` |
| Windows | `%APPDATA%\SafeCodeSessionGuard\settings.json` | `%APPDATA%\SafeCodeSessionGuard\logs\sessionguard.log` |
| Linux | `~/.config/SafeCodeSessionGuard/settings.json` | `~/.config/SafeCodeSessionGuard/logs/sessionguard.log` |

```json
{
  "method": "mouse",            // "mouse" | "key" | "none"
  "interval": 60,               // seconds, minimum 5
  "idle_only": true,
  "duration": 0,                // minutes, 0 = no limit
  "schedule_enabled": false,
  "schedule_start": "09:00",
  "schedule_end": "18:00",
  "schedule_days": [0, 1, 2, 3, 4],  // 0 = Monday
  "start_on_launch": true
}
```

The real file is plain JSON without comments. If a value is missing or invalid, the default is used.

### How it works

| | macOS | Windows | Linux |
|---|---|---|---|
| Sleep prevention | `caffeinate -dims -w <pid>` | `SetThreadExecutionState` | `systemd-inhibit --what=idle:sleep` |
| Idle time | `CGEventSourceSecondsSinceLastEventType` | `GetLastInputInfo` | `xprintidle` |
| Launch at login | `~/Library/LaunchAgents/com.safecodeg.sessionguard.plist` | `HKCU\…\Run` | `~/.config/autostart/safecode-sessionguard.desktop` |

## Building from source

Requires **Python 3.12**.

### Cross-platform builds

PyInstaller **cannot cross-compile**: a macOS build has to be made on macOS, a Windows build on
Windows and a Linux build on Linux. There are three ways to build:

1. **CI (recommended).** Every push to `main` runs lint, tests, a build and a launch smoke test on
   all three OSes in GitHub Actions, plus the Docker Linux build. The binaries are attached to
   the run as artifacts. Pushing a tag `vX.Y.Z` also publishes a GitHub Release with all of them.
2. **Locally,** on each OS:

| OS | Command | Output in `dist/` |
|---|---|---|
| macOS | `scripts/build_macos.sh` | `SafeCode SessionGuard.app`, `…-macos-arm64.zip`, `…-macos-arm64.dmg` |
| Windows (PowerShell 7) | `scripts\build_windows.ps1` | `SafeCodeSessionGuard\SafeCodeSessionGuard.exe`, `…-windows-x64.zip` |
| Linux | `scripts/build_linux.sh` | `SafeCodeSessionGuard/SafeCodeSessionGuard`, `…-linux-x86_64.tar.gz` |

3. **Linux from any OS with Docker.** This works from macOS, Windows/WSL or Linux:
   `scripts/build_linux_docker.sh amd64` (or `arm64`). It builds inside Ubuntu 24.04 and writes
   `dist/SafeCodeSessionGuard-<ver>-linux-<arch>.tar.gz`. CI runs this script too, so it stays
   working.

Windows binaries can only be built on Windows, or by CI. There's no supported way to build them
on macOS or Linux.

Native Linux builds need these system packages first (Debian/Ubuntu):

```bash
sudo apt-get install libgirepository-2.0-dev libcairo2-dev pkg-config gir1.2-ayatanaappindicator3-0.1
```

The architecture follows the machine you build on. The macOS app is `arm64` on Apple Silicon;
build on an Intel Mac for `x86_64`.

To check a build actually launches:
`python scripts/smoke_test.py <path-to-executable>`.

### Develop

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python session_guard.py      # run from source
.venv/bin/python -m pytest -q          # tests
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

### Release

1. Bump `__version__` in `sessionguard/__init__.py` and add an entry to `CHANGELOG.md`.
2. Commit, then `git tag vX.Y.Z && git push origin main vX.Y.Z`.
3. CI builds all three platforms and publishes the GitHub Release.

### Project layout

```
sessionguard/
  app.py          tray menu and app lifecycle
  guard.py        on/off, time limit and active-hours logic
  inhibitor.py    OS sleep prevention
  keepalive.py    mouse / key nudges
  idle.py         OS idle-time queries
  schedule.py     active-hours window
  settings.py     JSON settings with validation
  autostart.py    launch at login
  instance.py     single-instance lock
  logs.py         rotating log file and crash capture
  permissions.py  macOS Accessibility check
  icon.py         tray icon artwork
assets/           app icons (generated by scripts/make_icons.py)
scripts/          build (native + Docker), DMG, icon and smoke-test scripts
docker/           Linux build image
tests/            pytest suite
```

## Notice

SafeCode SessionGuard overrides idle screen-lock and sleep settings. Check your organisation's
IT and security policy before using it on a managed device.

© 2026 SafeCode Group · https://www.safecodeg.com/
