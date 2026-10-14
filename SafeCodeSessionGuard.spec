# PyInstaller spec for all platforms.
#   macOS   -> dist/SafeCode SessionGuard.app (menu-bar only, no Dock icon)
#   Windows -> dist/SafeCodeSessionGuard/SafeCodeSessionGuard.exe
#   Linux   -> dist/SafeCodeSessionGuard/SafeCodeSessionGuard
import re
import sys
from pathlib import Path

ROOT = Path(SPECPATH)
META = (ROOT / "sessionguard" / "__init__.py").read_text()


def meta(name):
    return re.search(rf'^{name} = "([^"]+)"', META, re.M).group(1)


VERSION, APP_NAME, APP_ID, BUNDLE_ID = (meta(n) for n in ("__version__", "APP_NAME", "APP_ID", "BUNDLE_ID"))
ICON = str(ROOT / "assets" / ("icon.icns" if sys.platform == "darwin" else "icon.ico"))

# Backends are picked at runtime by name. PyInstaller's pystray/pynput hooks
# find them by importing the packages, which fails on a headless build machine,
# so list them explicitly.
HIDDEN = {
    "darwin": ["pystray._darwin", "pynput.mouse._darwin", "pynput.keyboard._darwin", "pynput._util.darwin"],
    "win32": ["pystray._win32", "pynput.mouse._win32", "pynput.keyboard._win32", "pynput._util.win32"],
}.get(
    sys.platform,
    [
        "pystray._appindicator",
        "pystray._gtk",
        "pystray._xorg",
        "pystray._util.gtk",
        "pynput.mouse._xorg",
        "pynput.keyboard._xorg",
        "pynput._util.xorg",
        "pynput._util.xorg_keysyms",
    ],
)

a = Analysis(["session_guard.py"], hiddenimports=HIDDEN)


def linux_typelib_closure(namespaces):
    """Paths of every typelib the tray needs, transitive dependencies included.

    PyInstaller's GI hooks only bundle typelibs of namespaces that have their
    own hook, so dependencies like DBus-1.0 are left out and the app fails on
    systems without the matching gir1.2-* packages.
    """
    import gi

    try:
        gi.require_version("GIRepository", "3.0")
        from gi.repository import GIRepository

        repo = GIRepository.Repository()
        lazy = GIRepository.RepositoryLoadFlags.LAZY
    except ValueError:
        gi.require_version("GIRepository", "2.0")
        from gi.repository import GIRepository

        repo = GIRepository.Repository.get_default()
        lazy = GIRepository.RepositoryLoadFlags.IREPOSITORY_LOAD_FLAG_LAZY
    for namespace, version in namespaces:
        repo.require(namespace, version, lazy)
    return sorted({repo.get_typelib_path(ns) for ns in repo.get_loaded_namespaces()})


if sys.platform.startswith("linux"):
    bundled = {dest for dest, _, _ in a.datas}
    for path in linux_typelib_closure([("AyatanaAppIndicator3", "0.1"), ("Gtk", "3.0")]):
        dest = "gi_typelibs/" + Path(path).name
        if dest not in bundled:
            print(f"Bundling typelib dependency {dest}")
            a.datas.append((dest, path, "DATA"))
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_ID,
    console=False,
    icon=ICON,
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_ID)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=ICON,
        bundle_identifier=BUNDLE_ID,
        version=VERSION,
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleVersion": VERSION,
            "LSUIElement": True,
            "LSMinimumSystemVersion": "11.0",
            "NSHighResolutionCapable": True,
            "NSHumanReadableCopyright": "© 2026 SafeCode Group. https://www.safecodeg.com/",
        },
    )
