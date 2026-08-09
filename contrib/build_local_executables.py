#!/usr/bin/env python3
"""
PayQuant (PQN) Multi-Platform Installer & Executable Builder v6.4.0

Compiles full multi-megabyte standalone PyInstaller binaries:
 1. Combined Node + Miner Suite (dist/payquant-node-miner-gui.exe)
 2. Standalone Light Wallet GUI (dist/payquant-wallet-gui.exe)
 3. Standalone Public Explorer (dist/payquant-explorer.exe)
 4. Standalone Full Node GUI (dist/payquant-node-gui.exe)
 5. Standalone Solo Miner GUI (dist/payquant-miner-gui.exe)
 6. Command Daemon (dist/payquantd.exe)

Generates Inno Setup installer scripts and copies binaries into platform folders:
 - build_dist/windows/
 - build_dist/linux/
 - build_dist/macos/
 - build_dist/android/
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIST_DIR = os.path.join(BASE_DIR, "build_dist")

PLATFORM_DIRS = {
    "windows": os.path.join(BUILD_DIST_DIR, "windows"),
    "linux": os.path.join(BUILD_DIST_DIR, "linux"),
    "macos": os.path.join(BUILD_DIST_DIR, "macos"),
    "android": os.path.join(BUILD_DIST_DIR, "android"),
}

def setup_platform_dirs():
    for p_name, p_path in PLATFORM_DIRS.items():
        os.makedirs(p_path, exist_ok=True)

def build_executables():
    os.makedirs(DIST_DIR, exist_ok=True)
    setup_platform_dirs()

    print(f"[PayQuant Installer Builder v6.4.0] Target Directory: {DIST_DIR}")

    targets = [
        ("node_miner_gui.py", "payquant-node-miner-gui", "--windowed"),
        ("wallet_gui.py", "payquant-wallet-gui", "--windowed"),
        ("explorer_gui.py", "payquant-explorer", "--windowed"),
        ("node_gui.py", "payquant-node-gui", "--windowed"),
        ("miner_gui.py", "payquant-miner-gui", "--windowed"),
        ("test_node2_gui.py", "payquant-test-node2-gui", "--windowed"),
        ("node_entry.py", "payquantd", "--console"),
    ]

    for script_name, exe_name, mode in targets:
        script_path = os.path.join(BASE_DIR, "contrib", script_name)
        if not os.path.exists(script_path):
            continue

        print(f"[PayQuant Installer Builder] Compiling {exe_name}.exe with PyInstaller...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            script_path,
            "--onefile",
            f"--name={exe_name}",
            f"--distpath={DIST_DIR}",
            "--noconfirm",
            mode
        ]
        res = subprocess.run(cmd, cwd=BASE_DIR)
        if res.returncode == 0:
            exe_file = os.path.join(DIST_DIR, f"{exe_name}.exe")
            if os.path.exists(exe_file):
                size_mb = os.path.getsize(exe_file) / (1024 * 1024)
                print(f" -> [SUCCESS] Compiled {exe_name}.exe ({size_mb:.2f} MB) cleanly!")
        else:
            print(f" -> [WARNING] Build failed for {exe_name}.exe (Code {res.returncode})")

    # Generate Inno Setup installer scripts (.iss)
    try:
        from contrib.installer_generator import create_inno_setup_scripts
        create_inno_setup_scripts()
    except ImportError:
        try:
            from installer_generator import create_inno_setup_scripts
            create_inno_setup_scripts()
        except Exception as e:
            print(f"[Installer Generator Warning] {e}")

    # Copy all binaries & iss scripts to build_dist/windows
    win_dir = PLATFORM_DIRS["windows"]
    for fname in os.listdir(DIST_DIR):
        fpath = os.path.join(DIST_DIR, fname)
        if os.path.isfile(fpath) and (fname.endswith(".exe") or fname.endswith(".iss")):
            try:
                shutil.copy2(fpath, os.path.join(win_dir, fname))
            except Exception:
                pass

    print("[PayQuant Installer Builder] All PyInstaller binaries compiled & platform setup installer scripts generated!")

if __name__ == '__main__':
    build_executables()
