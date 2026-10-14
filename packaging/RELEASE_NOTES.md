## Downloads

| Your computer | Download |
|---|---|
| **Mac with Apple Silicon** (M1, M2, M3, M4, M5) | `SafeCodeSessionGuard-{version}-macos-apple-silicon.dmg` |
| **Mac with Intel** processor | `SafeCodeSessionGuard-{version}-macos-intel.dmg` |
| **Windows 10/11, 64-bit** (Intel / AMD) | `SafeCodeSessionGuard-{version}-windows-x64.zip` |
| **Windows 10, 32-bit** | `SafeCodeSessionGuard-{version}-windows-x86.zip` |
| **Windows 11 on ARM** (Snapdragon, Surface Pro X) | `SafeCodeSessionGuard-{version}-windows-arm64.zip` |
| **Ubuntu 22.04+, Debian 12+, Linux Mint 21+, Pop!_OS** (64-bit PC) | `safecode-sessionguard_{version}_amd64.deb` |
| **Ubuntu / Debian on ARM64**, Raspberry Pi OS 64-bit | `safecode-sessionguard_{version}_arm64.deb` |
| **Raspberry Pi OS 32-bit** (Bookworm or newer) | `safecode-sessionguard_{version}_armhf.deb` |
| **Debian 12+ 32-bit PC** (i386) | `safecode-sessionguard_{version}_i386.deb` |
| **Fedora, RHEL / Rocky / Alma 9+, openSUSE** (64-bit PC) | `safecode-sessionguard-{version}-1.x86_64.rpm` |
| **Fedora / RHEL on ARM64** | `safecode-sessionguard-{version}-1.aarch64.rpm` |
| **Any other Linux** (Arch, Manjaro, …): 64-bit PC / ARM64 / ARM 32-bit / 32-bit PC | `SafeCodeSessionGuard-{version}-linux-x86_64.tar.gz` / `-linux-aarch64.tar.gz` / `-linux-armv7l.tar.gz` / `-linux-i686.tar.gz` |

The macOS `.zip` files contain the same app as the `.dmg`.

**Install on Ubuntu/Debian:** `sudo apt install ./safecode-sessionguard_{version}_amd64.deb`
**Install on Fedora:** `sudo dnf install ./safecode-sessionguard-{version}-1.x86_64.rpm`

**Which one do I need?** Mac: Apple menu → About This Mac ("Chip: Apple M…" = Apple Silicon).
Windows: Settings → System → About → System type. Linux: run `uname -m` or `dpkg --print-architecture`.

Full install instructions: see the [README](https://github.com/SafeCodeGroup/SafeCode-SessionGuard#install).
Every file was built natively for its CPU and passed an automated self-test and launch test.

