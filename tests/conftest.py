import os
import sys
from pathlib import Path

# Headless backends so tests run in CI without a display or tray.
os.environ.setdefault("PYSTRAY_BACKEND", "dummy")
os.environ.setdefault("PYNPUT_BACKEND", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
