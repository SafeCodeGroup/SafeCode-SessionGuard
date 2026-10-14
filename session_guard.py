"""Entry point used by PyInstaller and `python session_guard.py`."""

import sys

from sessionguard.app import main

if __name__ == "__main__":
    sys.exit(main())
