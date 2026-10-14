"""macOS Accessibility permission, required to post synthetic mouse/key events."""

import platform
import subprocess

SYSTEM = platform.system()
SETTINGS_URL = "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"


def input_allowed(system: str = SYSTEM) -> bool:
    if system != "Darwin":
        return True
    try:
        from HIServices import AXIsProcessTrusted

        return bool(AXIsProcessTrusted())
    except Exception:
        return True  # can't tell; don't nag


def request_input_permission(system: str = SYSTEM) -> None:
    """Show the system prompt and open the Accessibility settings pane."""
    if system != "Darwin":
        return
    try:
        from HIServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt

        AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True})
    except Exception:
        pass
    subprocess.Popen(["open", SETTINGS_URL])
