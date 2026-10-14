"""Launch SessionGuard and check it really started and keeps running.

Usage: python scripts/smoke_test.py <command> [args...]
       e.g. smoke_test.py dist/SafeCodeSessionGuard/SafeCodeSessionGuard
            smoke_test.py .venv/bin/python session_guard.py
Set SMOKE_SECONDS to change the wait (default 8).

Passes only if the process is still running AND its log shows the guard
engaged with no fatal errors (a crashed app can linger as a hung process).
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main() -> int:
    cmd = sys.argv[1:]
    if not cmd:
        print(__doc__)
        return 2
    seconds = float(os.environ.get("SMOKE_SECONDS", "8"))
    log_dir = Path(tempfile.mkdtemp(prefix="sessionguard-smoke-"))
    env = dict(os.environ, SESSIONGUARD_LOG_DIR=str(log_dir))
    proc = subprocess.Popen(cmd, env=env)
    time.sleep(seconds)
    code = proc.poll()
    log_file = log_dir / "sessionguard.log"
    log = log_file.read_text(encoding="utf-8") if log_file.exists() else ""

    problems = []
    if code is not None:
        problems.append(f"exited after <{seconds:g}s with code {code}")
    if "Engaged" not in log:
        problems.append("log does not show the guard engaged")
    if "CRITICAL" in log:
        problems.append("log contains a fatal error")

    if code is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    name = " ".join(cmd)
    if problems:
        print(f"FAIL: {name}: " + "; ".join(problems))
        print(f"--- app log ({log_file}) ---\n{log or '(empty)'}")
        return 1
    print(f"PASS: {name} running after {seconds:g}s, guard engaged, no fatal errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
