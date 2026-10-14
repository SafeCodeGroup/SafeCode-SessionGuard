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

Download the file for your system from the
[Releases page](https://github.com/SafeCodeGroup/SafeCode-SessionGuard/releases). Every release
contains macOS, Windows and Linux builds.

| System | Hardware | Download |
|---|---|---|
| macOS 11+ | Apple Silicon (M1–M4) | `SafeCodeSessionGuard-<version>-macos-arm64.dmg` (or `.zip`) |
| macOS 11+ | Intel | `SafeCodeSessionGuard-<version>-macos-x86_64.dmg` (or `.zip`) |
| Windows 10 / 11 | Intel / AMD 64-bit | `SafeCodeSessionGuard-<version>-windows-x64.zip` |
| Windows 11 | ARM64 (Snapdragon, Surface Pro X) | `SafeCodeSessionGuard-<version>-windows-arm64.zip` |
| Ubuntu 24.04+, Debian 13+, Fedora 40+, Arch | Intel / AMD 64-bit | `SafeCodeSessionGuard-<version>-linux-x86_64.tar.gz` |
| Ubuntu 24.04+, Debian 13+, Fedora 40+ | ARM64 (Raspberry Pi 4/5 with 64-bit OS, ARM servers) | `SafeCodeSessionGuard-<version>-linux-aarch64.tar.gz` |

Not sure which one you need?
- **macOS:** Apple menu → **About This Mac**. "Chip: Apple M…" means Apple Silicon; "Processor: Intel" means Intel.
- **Windows:** Settings → System → About → **System type** says "x64-based" or "ARM-based".
- **Linux:** run `uname -m`. `x86_64` → x86_64 download, `aarch64` → aarch64 download.

Older Linux (for example Ubuntu 22.04, which has glibc older than 2.39): see
[Run from source](#run-from-source-any-os-older-linux-intel-mac).

### macOS

1. Open the `.dmg` and drag **SafeCode SessionGuard** onto **Applications**.
   If you downloaded the `.zip`, unzip it and move the app into **Applications**.
2. **First launch.** The app isn't notarized yet, so macOS blocks a plain double-click.
   - In Finder, open **Applications**, right-click **SafeCode SessionGuard** → **Open** →
     **Open**, or
   - run this in Terminal:
     ```bash
     xattr -dr com.apple.quarantine "/Applications/SafeCode SessionGuard.app"
     open "/Applications/SafeCode SessionGuard.app"
     ```
3. A green shield appears in the **menu bar** at the top of the screen. There is no Dock icon.
4. **Allow input** so the mouse/key nudge works: go to **System Settings → Privacy & Security →
   Accessibility** and turn on **SafeCode SessionGuard**. Until you do, the menu shows
   "⚠ Allow input in Accessibility settings…" as a shortcut. Sleep prevention works without this.
5. Optional: choose **Launch at login** from the menu. This only works once the app is in
   **Applications**, not while it's running from the DMG.

### Ubuntu / Debian

```bash
# 1. Tray support. Ubuntu's desktop already includes it; this is a no-op there.
sudo apt install gir1.2-ayatanaappindicator3-0.1 xprintidle

# 2. Download and install for your user (no root needed)
tar -xzf SafeCodeSessionGuard-*-linux-$(uname -m).tar.gz
./SafeCodeSessionGuard/install.sh

# 3. Start it from the app menu ("SafeCode SessionGuard") or:
safecode-sessionguard &
```

`install.sh` installs:

| What | Where |
|---|---|
| App | `~/.local/opt/SafeCodeSessionGuard/` |
| Command | `~/.local/bin/safecode-sessionguard` |
| Menu entry | `~/.local/share/applications/safecode-sessionguard.desktop` |
| Icon | `~/.local/share/icons/hicolor/256x256/apps/` |

To upgrade, extract the new download and run its `install.sh` again.

**Tray icon not showing?**
- **Ubuntu (GNOME):** the "Ubuntu AppIndicators" extension is enabled by default.
- **Plain GNOME (Fedora, Debian GNOME):** install and enable the
  [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/)
  extension, e.g. `sudo apt install gnome-shell-extension-appindicator` on Debian, then log out
  and back in.
- **KDE Plasma, XFCE, Cinnamon, MATE, Budgie:** tray support is built in.

### Fedora / Arch / other Linux

Same download and `install.sh` as above. Only the package names for tray support and idle
detection differ:

```bash
sudo dnf install libayatana-appindicator-gtk3 xprintidle          # Fedora
sudo pacman -S libayatana-appindicator xprintidle                  # Arch / Manjaro
```

`xprintidle` is optional. It powers **Only when idle** on X11. On Wayland, and when it's missing,
the app falls back to a fixed timer. Sleep prevention uses `systemd-inhibit`, which every
systemd distro includes.

### Windows

Unzip `SafeCodeSessionGuard-<version>-windows-x64.zip` (or `-windows-arm64.zip` on ARM PCs) anywhere (for example
`C:\Program Files\SafeCodeSessionGuard`) and run `SafeCodeSessionGuard.exe`. The build isn't
code-signed yet, so on the SmartScreen prompt choose **More info → Run anyway**. The icon appears
in the system tray; Windows may tuck it under the **^** overflow arrow.

### Run from source (any OS, older Linux, Intel Mac)

Requires Python 3.10 or newer. CI tests this route on Ubuntu 22.04 with its system Python 3.10.

```bash
git clone https://github.com/SafeCodeGroup/SafeCode-SessionGuard.git
cd SafeCode-SessionGuard
```

- **macOS (Intel or Apple Silicon) and Windows**
  ```bash
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt     # Windows: .venv\Scripts\pip ...
  .venv/bin/python session_guard.py              # Windows: .venv\Scripts\pythonw session_guard.py
  ```
- **Linux.** This uses your distro's PyGObject. A compiler is needed only for the small `evdev`
  module that `pynput` depends on:
  ```bash
  sudo apt install python3-venv python3-dev build-essential python3-gi \
       gir1.2-ayatanaappindicator3-0.1 xprintidle                     # Ubuntu/Debian
  # Fedora: sudo dnf install python3-devel gcc python3-gobject libayatana-appindicator-gtk3 xprintidle
  python3 -m venv --system-site-packages .venv
  .venv/bin/pip install pystray==0.19.5 pynput==1.8.2 Pillow
  .venv/bin/python session_guard.py &
  ```

### Uninstall

| OS | Steps |
|---|---|
| macOS | Quit from the menu, delete `/Applications/SafeCode SessionGuard.app`, then `rm -f ~/Library/LaunchAgents/com.safecodeg.sessionguard.plist`. Optionally remove `~/Library/Application Support/SafeCodeSessionGuard` and `~/Library/Logs/SafeCodeSessionGuard`. |
| Linux | `~/.local/opt/SafeCodeSessionGuard/install.sh --uninstall`. Optionally remove `~/.config/SafeCodeSessionGuard`. |
| Windows | Turn off **Launch at login**, quit, delete the folder. Optionally remove `%APPDATA%\SafeCodeSessionGuard`. |

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

Release builds use **Python 3.12**.

### Cross-platform builds

PyInstaller **cannot cross-compile**: a macOS build has to be made on macOS, a Windows build on
Windows and a Linux build on Linux. There are three ways to build:

1. **CI (recommended).** `.github/workflows/ci.yml` has a single `build` job that runs natively
   on six targets:

   | OS | CPU |
   |---|---|
   | macOS | Apple Silicon, Intel |
   | Windows | x64, ARM64 |
   | Linux | x86_64, ARM64 |

   Each target lints, tests, builds, checks the binary's CPU architecture, then runs `--self-test`
   and a launch test. The Linux targets also:
   - install and launch the download on Ubuntu 24.04, Debian 13 and Fedora (plus Arch on x86_64);
   - run from source on Ubuntu 22.04.

   Binaries are attached to every run as artifacts. On a `vX.Y.Z` tag the same job publishes all
   eight files to one GitHub Release.
2. **Locally,** on each OS:

| OS | Command | Output in `dist/` |
|---|---|---|
| macOS | `scripts/build_macos.sh` | `SafeCode SessionGuard.app`, `…-macos-<arm64\|x86_64>.zip` and `.dmg` |
| Windows (PowerShell 7) | `scripts\build_windows.ps1` | `SafeCodeSessionGuard\SafeCodeSessionGuard.exe`, `…-windows-<x64\|arm64>.zip` |
| Linux | `scripts/build_linux.sh` | `SafeCodeSessionGuard/SafeCodeSessionGuard`, `…-linux-<x86_64\|aarch64>.tar.gz` |

3. **Linux from any OS with Docker.** This works from macOS, Windows/WSL or Linux:
   `scripts/build_linux_docker.sh amd64` (or `arm64`). It builds inside Ubuntu 24.04 and writes
   `dist/SafeCodeSessionGuard-<ver>-linux-<arch>.tar.gz`. CI runs this script too, so it stays
   working.

Windows binaries can only be built on Windows, or by CI. There's no supported way to build them
on macOS or Linux.

Native Linux builds need these system packages first (Debian/Ubuntu):

```bash
sudo apt-get install libgirepository-2.0-dev libcairo2-dev pkg-config \
    gir1.2-ayatanaappindicator3-0.1 gir1.2-girepository-3.0
```

The binary's CPU architecture is always the one of the machine you build on. CI builds each of
the six targets natively: macOS arm64 and x86_64, Windows x64 and ARM64, Linux x86_64 and
aarch64.

To check a build:
- `<executable> --self-test report.txt` loads every runtime dependency (tray backend, input
  backends, OS APIs) inside the built binary. It exits with 0 and writes `OK` when everything
  is there.
- `python scripts/smoke_test.py <executable>` checks the app stays running.

On Linux, run both under a display (`xvfb-run` on headless machines).

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
3. CI builds and tests all three platforms. Each platform uploads its files to a draft release,
   and the release is published automatically once all eight files are attached
   (macOS arm64/x86_64 `.dmg` + `.zip`, Windows x64/arm64 `.zip`, Linux x86_64/aarch64 `.tar.gz`).

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
  compat.py       shims for third-party library changes
  instance.py     single-instance lock
  logs.py         rotating log file and crash capture
  permissions.py  macOS Accessibility check
  icon.py         tray icon artwork
assets/           app icons (generated by scripts/make_icons.py)
scripts/          build (native + Docker), DMG, icon and smoke-test scripts
docker/           Linux build image
packaging/linux/  install.sh shipped inside the Linux download
tests/            pytest suite
```

## Notice

SafeCode SessionGuard overrides idle screen-lock and sleep settings. Check your organisation's
IT and security policy before using it on a managed device.

© 2026 SafeCode Group · https://www.safecodeg.com/
