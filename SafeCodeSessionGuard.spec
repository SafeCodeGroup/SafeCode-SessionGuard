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

a = Analysis(["session_guard.py"])
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
