#!/usr/bin/env python3
"""
PayQuant (PQN) Miner / Node System Service Installer v6.4.0 (FS-02-03)

Auto-start mining (and/or the node daemon) as a proper background service on:
  * Windows  - native Windows Service (win32serviceutil) w/ NSSM fallback
  * Linux    - systemd unit file
  * macOS    - launchd plist

Usage:
  python install_service.py --service=miner install
  python install_service.py --service mined remove
  python install_service.py --status

Pure-stdlib except on Windows service mode (win32serviceutil - optional,
falls back to a generated .bat launched at startup).
"""

import argparse
import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVICE_NAME = "PayQuantMiner"
SERVICE_DISPLAY = "PayQuant (PQN) Solo Miner Service"


def _entry_point(service):
    """Return the Python entry module for a service."""
    if service == "miner":
        return os.path.join(BASE_DIR, "contrib", "miner_gui.py")
    if service == "node":
        return os.path.join(BASE_DIR, "contrib", "node_entry.py")
    if service == "node_miner":
        return os.path.join(BASE_DIR, "contrib", "node_miner_gui.py")
    raise SystemExit(f"Unknown service: {service}")


def _python():
    return sys.executable or "python"


def install_linux(unit_name, command):
    """systemd user/service unit file."""
    service_path = f"/etc/systemd/system/{unit_name}.service"
    unit = f"""[Unit]
Description={SERVICE_DISPLAY}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={BASE_DIR}
ExecStart={command}
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    if os.geteuid() == 0:
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(unit)
        subprocess.run(["systemctl", "daemon-reload"], check=False)
        print(f"[install] systemd unit installed: {service_path}")
        return
    # user-level fallback
    user_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(user_dir, exist_ok=True)
    user_path = os.path.join(user_dir, f"{unit_name}.service")
    with open(user_path, "w", encoding="utf-8") as f:
        f.write(unit)
    print(f"[install] user systemd unit installed: {user_path}")


def install_launchd(unit_name):
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.payquant.{unit_name}.plist")
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.payquant.{unit_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable or 'python'}</string>
        <string>{entry_name}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{BASE_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{os.path.expanduser('~/Library/Logs/payquant-miner.log')}</string>
    <key>StandardErrorPath</key>
    <string>{os.path.expanduser('~/Library/Logs/payquant-node.log')}</string>
</dict>
</plist>
"""
    os.makedirs(os.path.dirname(plist_path), exist_ok=True)
    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist)
    subprocess.run(["launchctl", "load", plist_path], check=False)
    print(f"[install] launchd agent installed: {plist_path}")


def install_windows(entry_name, service="miner"):
    try:
        import win32serviceutil  # pywin32
        import win32service
        import win32event
    except ImportError:
        _windows_bat_fallback(entry_name, service)
        return False

    class PayquantMinerService(win32serviceutil.ServiceFramework):
        _svc_name_ = "PayQuantMiner"
        _svc_display_name_ = SERVICE_DISPLAY
        _svc_description_ = "PayQuant (PQN) background miner service"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self):
            cmd = [_python(), entry_name]
            while True:
                p = subprocess.Popen(cmd, cwd=BASE_DIR)
                rc = win32event.WaitForSingleObject(self.hWaitStop, 30000)
                if rc == win32event.WAIT_OBJECT_0:
                    p.terminate()
                    break

    win32serviceutil.HandleCommandLine(PayquantMinerService)


def _windows_nssm_fallback(entry_name, service):
    nssm = shutil.which("nssm")
    if not nssm:
        bat = os.path.join(BASE_DIR, f"payquant-{service}-service.bat")
        content = f"@echo off\r\ncd /d {BASE_DIR}\r\n\"{_python()}\" \"{entry_name}\"\r\n"
        with open(bat, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[WARN] pywin32/nssm not found; wrote bat autostart: {bat}")
        return
    subprocess.run([nssm, "install", "PayQuantMiner", _python(), entry_name], check=False)
    subprocess.run([nssm, "start", "PayQuantMiner"], check=False)
    print("[install] NSSM Windows service installed.")


def remove_service():
    if sys.platform == "linux":
        subprocess.run(["systemctl", "disable", "--now", f"{SERVICE_NAME}.service"], check=False)
        subprocess.run(["rm", "-f", f"/etc/systemd/system/{SERVICE_NAME}.service"], check=False)
        print("[+] systemd service removed.")
    elif sys.platform == "darwin":
        plist = os.path.expanduser(f"~/Library/LaunchAgents/com.payquant.miner.plist")
        subprocess.run(["launchctl", "unload", plist], check=False)
        try:
            os.remove(plist)
        except OSError:
            pass
        print("[+] launchd agent removed.")
    else:
        try:
            import win32serviceutil
            win32serviceutil.StopService(SERVICE_NAME)
            win32serviceutil.RemoveService(SERVICE_NAME)
            print("[+] Windows service removed.")
        except ImportError:
            print("[!] pywin32 not installed; remove manually or use nssm remove PayQuantMiner")


def print_status():
    if sys.platform == "linux":
        subprocess.run(["systemctl", "is-active", f"{SERVICE_NAME}.service"], check=False)
    elif sys.platform == "darwin":
        subprocess.run(["launchctl", "list"], check=False)
    else:
        try:
            import win32serviceutil
            win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        except ImportError:
            print("pywin32 missing; run `sc query PayQuantMiner` to inspect.")


def main():
    parser = argparse.ArgumentParser(description="PayQuant system service installer")
    parser.add_argument("action", choices=["install", "remove", "status"], help="Action")
    parser.add_argument("--service", choices=["miner", "node", "node_miner"], default="miner",
                        help="Which daemon to register as a service")
    parser.add_argument("-f", "--forward", action="store_true", help="(unused, reserved)")
    args = parser.parse_args()

    entry_name = _entry_point(args.service)
    service = args.service

    if args.action == "install":
        if sys.platform == "linux":
            install_linux(f"payquant-{service}",
                          f"{_python()} -- \"{entry_name}\"" if "miner_gui" in entry_name else f"{_python()} \"{entry_name}\"")
        elif sys.platform == "darwin":
            install_launchd(entry_name)
        else:
            install_windows(entry_name, service)
        print(f"[OK] {service.title()} service installed & configured.")
    elif args.action == "remove":
        remove_service()
    else:
        print_status()


if __name__ == "__main__":
    main()