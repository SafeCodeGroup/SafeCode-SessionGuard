"""Single-instance lock so two copies never fight over the tray and inhibitor."""

import os
from pathlib import Path


class SingleInstance:
    def __init__(self, path):
        self.path = Path(path)
        self._fh = None

    def acquire(self) -> bool:
        """Take the lock. Returns False if another instance holds it."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.path, "a+")
        try:
            if os.name == "nt":
                import msvcrt

                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            return False
        self._fh = fh
        return True

    def release(self) -> None:
        # Closing the handle releases the lock on every platform.
        if self._fh is not None:
            self._fh.close()
            self._fh = None
