#!/usr/bin/env python3
"""
PayQuant (PQN) autonomous self-healing test loop v2.0.0-quantum
===============================================================
Repeatedly runs the ecosystem test suite until green (or an attempt budget is
reached), healing non-destructive environment breakage between runs. After a
green suite it enforces the secret gate before reporting DEPLOY READY.

Usage:
    python scripts/test_loop.py [--attempts N] [--wait SECONDS]
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = os.path.join(BASE_DIR, "scripts", "local_test_suite.py")
SEC_GATE = os.path.join(BASE_DIR, "scripts", "check_secrets.py")


def heal_pass():
    """Best-effort, non-destructive environment healing between runs."""
    # purge bytecode caches so a fresh interpreter picks up edited modules
    for root, dirs, _ in os.walk(BASE_DIR):
        if "__pycache__" in dirs:
            try:
                shutil.rmtree(os.path.join(root, "__pycache__"))
            except Exception:
                pass
    # regenerate the public 3D gallery only if it went missing
    gallery = os.path.join(BASE_DIR, "explorer_3d", "diamonds.json")
    if not os.path.exists(gallery):
        try:
            sys.path.insert(0, BASE_DIR)
            import tools.build_gallery3d
            tools.build_gallery3d.build_gallery(limit=64)
        except Exception:
            pass


def run_once():
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", SUITE],
            capture_output=True, text=True, cwd=BASE_DIR, env=env, timeout=600,
        )
    except subprocess.TimeoutExpired:
        return False, "test suite timed out"
    out = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and "PASSED" in out
    return ok, out


def secret_gate_ok():
    try:
        proc = subprocess.run(
            [sys.executable, SEC_GATE], capture_output=True, text=True,
            cwd=BASE_DIR, timeout=180,
        )
        return proc.returncode == 0
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=int, default=999,
                    help="max suite runs before giving up")
    ap.add_argument("--wait", type=float, default=2.0, help="seconds between runs")
    args = ap.parse_args()

    print("PayQuant autonomous self-healing loop (v2.0.0-quantum)", flush=True)
    for attempt in range(1, args.attempts + 1):
        print(f"--- attempt {attempt} ---", flush=True)
        ok, out = run_once()
        tail = "\n".join(out.strip().splitlines()[-6:]) if out.strip() else "(no output)"
        print(tail, flush=True)
        if ok:
            if secret_gate_ok():
                print("[self-healing] Tests green + secret gate clean.", flush=True)
                print("[self-healing] DEPLOY READY", flush=True)
                return 0
            print("[self-healing] tests green but secret gate FAILED - blocking deploy.",
                  flush=True)
            return 1
        heal_pass()
        time.sleep(max(0.25, args.wait))
    print("[self-healing] max attempts reached without a green suite.", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())