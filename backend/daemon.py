#!/usr/bin/env python3
"""
PayQuant (PQN) Daemon / Process Manager v6.6.0 (FS-03-02)

Runs the Node and Miner as genuine independent background processes
(NOT GUI threads), with unified lifecycle control.

  python backend/daemon.py start node|miner|api|signaling|all
  python backend/daemon.py stop  node|miner|api|signaling|all
  python backend/daemon.py status

Manages pidfiles under <userdata>/payquant_daemons/ and kills processes
cleanly, regardless of whether Node/Miner are running as GUI or CLI.

"""

import os
import sys
import json
import time
import signal
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DAEMON_DIR = os.path.join(os.environ.get(
    "PAYQUANT_DAEMON_DIR",
    os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "PayQuant", "daemons")
))

DAEMONS = {
    "node": {
        "cmd": [sys.executable, os.path.join(BASE_DIR, "contrib", "node_entry.py"), "--daemon"],
        "title": "PayQuant Full Node daemon"
    },
    "miner": {
        "cmd": [sys.executable, os.path.join(BASE_DIR, "contrib", "miner_gui.py")],
        "title": "PayQuant Solo Miner daemon"
    },
    "api": {
        "cmd": [sys.executable, os.path.join(BASE_DIR, "backend", "api_server.py")],
        "title": "PayQuant Unified API daemon"
    },
    "signaling": {
        "cmd": [sys.executable, os.path.join(BASE_DIR, "backend", "signaling_server.py")],
        "title": "PayQuant WebSocket Signaling daemon"
    }
}

PREFIX = "payquant-"
EXT = ".pid"


def _pidfile(name):
    return os.path.join(DAEMON_DIR, PREFIX + name + EXT)


def _ensure_dir():
    os.makedirs(DAEMON_DIR, exist_ok=True)


def _save_pid(name, pid):
    _ensure_dir()
    with open(_pidfile(name), "w", encoding="utf-8") as f:
        f.write(str(pid))


def _read_pid(name):
    path = _pidfile(name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return None


def _clear(name):
    try:
        os.remove(_pidfile(name))
    except OSError:
        pass


def _alive(pid):
    if not pid:
        return False
    if sys.platform == "win32":
        return _win_pid_exists(pid)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except (OSError, PermissionError):
        return True


def _win_pid_exists(pid):
    try:
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if h:
            ctypes.windll.kernel32.CloseHandle(h)
            return True
        return False
    except Exception:
        return True


def _force_kill(pid):
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def _term_kill(pid):
    if sys.platform == "win32":
        # no SIGTERM on Windows - use taskkill without /F then /F if needed
        subprocess.run(["taskkill", "/PID", str(pid), "/T"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


def start_one(name):
    if name not in DAEMONS:
        return False
    pid = _read_pid(name)
    if pid and _alive(pid):
        print(f"[status] {name}: already running (pid {pid})")
        return True
    spec = DAEMONS[name]
    log_path = os.path.join(DAEMON_DIR, f"{name}.log")
    _ensure_dir()
    with open(log_path, "a", encoding="utf-8") as logfile:
        proc = subprocess.Popen(
            spec["cmd"], stdin=subprocess.DEVNULL, stdout=logfile, stderr=logfile,
            start_new_session=True, cwd=BASE_DIR
        )
    _save_pid(name, proc.pid)
    print(f"[start] {name}: launched pid {proc.pid} ({spec['title']})")
    return True


def stop_one(name, graceful=True):
    if name not in DAEMONS:
        return False
    pid = _read_pid(name)
    if not pid or not _alive(pid):
        print(f"[stop] {name}: not running")
        _clear(name)
        return True
    try:
        if graceful:
            _term_kill(pid)
        deadline = time.time() + 6
        while time.time() < deadline and _alive(pid):
            time.sleep(0.25)
        if _alive(pid):
            _force_kill(pid)
    except Exception as e:
        print(f"[stop] {name}: error {e}")
    _clear(name)
    print(f"[stop] {name}: stopped (pid {pid})")
    return True


def status_all():
    print("PayQuant daemon status")
    print("-" * 40)
    for name in DAEMONS:
        pid = _read_pid(name)
        running = pid and _alive(pid)
        print(f"{name:<12} {'RUNNING' if running else 'stopped'}     pid {pid if running else '-'}")


def main():
    parser = argparse.ArgumentParser(description="PayQuant daemon / background-process manager")
    parser.add_argument("command", choices=["start", "stop", "status", "restart"], help="Command")
    parser.add_argument("target", nargs="?", default="all",
                        choices=["all", "node", "miner", "api", "signaling"], help="Which daemon")
    args = parser.parse_args()

    global log
    log = _mock_logger()

    targets = list(DAEMONS.keys()) if args.target == "all" else [args.target]

    if args.command == "start":
        for t in targets:
            if t in DAEMONS:
                start_one(t)
            else:
                print(f"[!] unknown daemon: {t}")
    elif args.command == "stop":
        for t in targets:
            if t in DAEMONS:
                stop_one(t)
            else:
                print(f"[!] unknown daemon: {t}")
    elif args.command == "restart":
        for t in targets:
            stop_one(t)
            start_one(t)
    else:
        status_all()
    return 0


class _mock_logger:
    @staticmethod
    def info(msg):
        sys.stderr.write(msg + "\n")


if __name__ == "__main__":
    log = _mock_logger()
    sys.exit(main())