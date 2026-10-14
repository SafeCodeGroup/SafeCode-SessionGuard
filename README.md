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

Download the file for your computer from the
[Releases page](https://github.com/SafeCodeGroup/SafeCode-SessionGuard/releases). Every release
has a native build for each of these:

| Your computer | Download |
|---|---|
| **Mac, Apple Silicon** (M1, M2, M3, M4, M5) | `SafeCodeSessionGuard-<version>-macos-apple-silicon.dmg` |
| **Mac, Intel** | `SafeCodeSessionGuard-<version>-macos-intel.dmg` |
| **Windows 10/11, 64-bit** (Intel / AMD) | `SafeCodeSessionGuard-<version>-windows-x64.zip` |
| **Windows 10, 32-bit** | `SafeCodeSessionGuard-<version>-windows-x86.zip` |
| **Windows 11 on ARM** (Snapdragon, Surface Pro X) | `SafeCodeSessionGuard-<version>-windows-arm64.zip` |
| **Ubuntu 22.04+, Debian 12+, Linux Mint 21+, Pop!_OS** (64-bit PC) | `safecode-sessionguard_<version>_amd64.deb` |
| **Ubuntu / Debian on ARM64**, Raspberry Pi OS 64-bit | `safecode-sessionguard_<version>_arm64.deb` |
| **Raspberry Pi OS 32-bit** (Bookworm or newer) | `safecode-sessionguard_<version>_armhf.deb` |
| **Debian 12+ 32-bit PC** (i386) | `safecode-sessionguard_<version>_i386.deb` |
| **Fedora, RHEL / Rocky / Alma 9+, openSUSE** (64-bit PC) | `safecode-sessionguard-<version>-1.x86_64.rpm` |
| **Fedora / RHEL on ARM64** | `safecode-sessionguard-<version>-1.aarch64.rpm` |
| **Any other Linux** (Arch, Manjaro, …) | `SafeCodeSessionGuard-<version>-linux-<x86_64\|aarch64\|armv7l\|i686>.tar.gz` |

macOS downloads also come as a `.zip` with the same app.

**Which one do I need?**
- **Mac:** Apple menu → **About This Mac**. "Chip: Apple M…" means Apple Silicon.
- **Windows:** Settings → System → About → **System type**.
- **Linux:** run `uname -m` (`x86_64`, `aarch64`, `armv7l` or `i686`) or
  `dpkg --print-architecture` (`amd64`, `arm64`, `armhf` or `i386`).

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

### Ubuntu, Debian, Linux Mint, Raspberry Pi OS (.deb)

```bash
sudo apt install ./safecode-sessionguard_*_amd64.deb      # use your architecture's file
safecode-sessionguard &                                    # or open it from the app menu
```

`apt` installs the one dependency (`libayatana-appindicator3-1`) automatically. You can also
double-click the `.deb` and install it with the **App Center** / **Software** app.

- Remove: `sudo apt remove safecode-sessionguard`
- Upgrade: install the newer `.deb` the same way.

### Fedora, RHEL / Rocky / Alma, openSUSE (.rpm)

```bash
sudo dnf install ./safecode-sessionguard-*-1.x86_64.rpm   # Fedora / RHEL family
sudo zypper install ./safecode-sessionguard-*-1.x86_64.rpm # openSUSE
safecode-sessionguard &
```

On RHEL / Rocky / Alma, enable EPEL first (`sudo dnf install epel-release`); it provides
`libayatana-appindicator-gtk3`.

- Remove: `sudo dnf remove safecode-sessionguard`

### Any other Linux (tarball, no root needed)

```bash
tar -xzf SafeCodeSessionGuard-*-linux-$(uname -m).tar.gz
./SafeCodeSessionGuard/install.sh                # installs to ~/.local for your user
safecode-sessionguard &
```

Install tray support from your distro first (Arch: `sudo pacman -S libayatana-appindicator`).
`install.sh` adds the app to `~/.local/opt/SafeCodeSessionGuard`, a `safecode-sessionguard`
command, a menu entry and an icon. `./install.sh --uninstall` removes them.

### Linux notes

- **Tray icon not showing?**
  - **Ubuntu (GNOME):** the "Ubuntu AppIndicators" extension is enabled by default.
  - **Plain GNOME (Fedora, Debian GNOME):** install and enable the
    [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/)
    extension, e.g. `sudo apt install gnome-shell-extension-appindicator` on Debian, then log out
    and back in.
  - **KDE Plasma, XFCE, Cinnamon, MATE, Budgie, LXQt, Raspberry Pi desktop:** tray support is
    built in.
- **Only when idle** uses `xprintidle` on X11 (`sudo apt install xprintidle`). On Wayland, and
  when it's missing, it falls back to a fixed timer.
- **Minimum versions:**
  - 64-bit builds need glibc 2.35 or newer (Ubuntu 22.04+, Debian 12+, Fedora 36+, RHEL 10).
  - 32-bit builds need glibc 2.36 or newer (Debian 12 / Raspberry Pi OS Bookworm).
  - On anything older, use [Run from source](#run-from-source-any-os-older-linux).

### Windows

Unzip `SafeCodeSessionGuard-<version>-windows-x64.zip` (`-windows-x86.zip` on 32-bit Windows,
`-windows-arm64.zip` on ARM PCs) anywhere (for example
`C:\Program Files\SafeCodeSessionGuard`) and run `SafeCodeSessionGuard.exe`. The build isn't
code-signed yet, so on the SmartScreen prompt choose **More info → Run anyway**. The icon appears
in the system tray; Windows may tuck it under the **^** overflow arrow.

### Run from source (any OS, older Linux)

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
| Linux | `.deb`: `sudo apt remove safecode-sessionguard` · `.rpm`: `sudo dnf remove safecode-sessionguard` · tarball: `~/.local/opt/SafeCodeSessionGuard/install.sh --uninstall`. Optionally remove `~/.config/SafeCodeSessionGuard`. |
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

1. **CI (recommended).** `.github/workflows/ci.yml` has a single `build` job that runs for nine
   targets:

   | OS | Targets |
   |---|---|
   | macOS | Apple Silicon, Intel |
   | Windows | x64, x86 32-bit, ARM64 |
   | Linux | x86_64, ARM64, ARMv7 32-bit, x86 32-bit |

   The 64-bit Linux builds run on Ubuntu 22.04 for glibc 2.35 compatibility. The 32-bit Linux
   builds run inside Debian 12 containers (QEMU for ARMv7). Each target builds natively, checks
   the binary's CPU architecture, then runs `--self-test` and a launch test.

   Linux targets also produce `.deb` packages (plus `.rpm` for 64-bit) and test them:
   - tarball and `.deb` install, launch and uninstall on Ubuntu 22.04/24.04 and Debian 12/13;
   - tarball and `.rpm` on Fedora;
   - tarball on Arch;
   - running from source on Ubuntu 22.04.

   On a `vX.Y.Z` tag the same job publishes all 17 files to one GitHub Release.
2. **Locally,** on each OS:

| OS | Command | Output in `dist/` |
|---|---|---|
| macOS | `scripts/build_macos.sh` | `SafeCode SessionGuard.app`, `…-macos-<apple-silicon\|intel>.zip` and `.dmg` |
| Windows (PowerShell 7) | `scripts\build_windows.ps1` | `SafeCodeSessionGuard\SafeCodeSessionGuard.exe`, `…-windows-<x64\|x86\|arm64>.zip` (follows the Python you build with) |
| Linux | `scripts/build_linux.sh` | `SafeCodeSessionGuard/`, `…-linux-<arch>.tar.gz`, `.deb`, and `.rpm` if `rpmbuild` is installed |
| Linux 32-bit (via Docker) | `scripts/ci/build_linux_debian.sh linux/arm/v7 armv7l` or `linux/386 i686` | `…-linux-armv7l.tar.gz` + `armhf.deb`, or `…-linux-i686.tar.gz` + `i386.deb` |

3. **Linux from any OS with Docker.** This works from macOS, Windows/WSL or Linux:
   `scripts/build_linux_docker.sh amd64` (or `arm64`). It builds inside Ubuntu 24.04 and writes
   `dist/SafeCodeSessionGuard-<ver>-linux-<arch>.tar.gz`. CI runs this script too, so it stays
   working.

Windows binaries can only be built on Windows, or by CI. There's no supported way to build them
on macOS or Linux.

Native Linux builds need these system packages first (Debian/Ubuntu):

```bash
sudo apt-get install libgirepository1.0-dev libcairo2-dev pkg-config \
    gir1.2-ayatanaappindicator3-0.1 gir1.2-girepository-2.0 rpm   # rpm: optional, for .rpm
```

The binary's CPU architecture is always the one of the machine (or container, or Python) you
build on.

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
   and the release is published automatically once all 17 files are attached:
   - macOS: 4
   - Windows: 3
   - Linux: 4 tarballs, 4 `.deb`, 2 `.rpm`

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
scripts/          build (native + Docker), DMG, .deb/.rpm, icon and smoke-test scripts
docker/           Linux build image
packaging/        Linux install.sh (tarball) and the GitHub release notes template
tests/            pytest suite
```

## Notice

SafeCode SessionGuard overrides idle screen-lock and sleep settings. Check your organisation's
IT and security policy before using it on a managed device.

© 2026 SafeCode Group · https://www.safecodeg.com/
