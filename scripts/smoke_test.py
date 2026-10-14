"""Launch a built SessionGuard binary and check it is still running after a while.

Usage: python scripts/smoke_test.py <path-to-executable> [seconds]
"""

import subprocess
import sys
import time


def main() -> int:
    exe = sys.argv[1]
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 8
    proc = subprocess.Popen([exe])
    time.sleep(seconds)
    code = proc.poll()
    if code is not None:
        print(f"FAIL: {exe} exited after <{seconds:g}s with code {code}")
        return 1
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    print(f"PASS: {exe} still running after {seconds:g}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
