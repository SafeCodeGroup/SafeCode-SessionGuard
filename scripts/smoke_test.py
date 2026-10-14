"""Launch SessionGuard and check it is still running after a while.

Usage: python scripts/smoke_test.py <command> [args...]
       e.g. smoke_test.py dist/SafeCodeSessionGuard/SafeCodeSessionGuard
            smoke_test.py .venv/bin/python session_guard.py
Set SMOKE_SECONDS to change the wait (default 8).
"""

import os
import subprocess
import sys
import time


def main() -> int:
    cmd = sys.argv[1:]
    if not cmd:
        print(__doc__)
        return 2
    seconds = float(os.environ.get("SMOKE_SECONDS", "8"))
    proc = subprocess.Popen(cmd)
    time.sleep(seconds)
    code = proc.poll()
    if code is not None:
        print(f"FAIL: {' '.join(cmd)} exited after <{seconds:g}s with code {code}")
        return 1
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    print(f"PASS: {' '.join(cmd)} still running after {seconds:g}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
