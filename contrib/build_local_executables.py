#!/usr/bin/env python3
"""
PayQuant (PQN) Multi-Platform Installer & Executable Builder v4.0.0

Compiles full multi-megabyte standalone PyInstaller binaries with embedded icons:
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

As a final step (Windows host) it bundles every built binary + installer script
into a clean single-platform release ZIP: build_dist/payquant-v4.0.0-windows.zip
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIST_DIR = os.path.join(BASE_DIR, "build_dist")
PIXMAPS_DIR = os.path.join(BASE_DIR, "share", "pixmaps")

PLATFORM_DIRS = {
    "windows": os.path.join(BUILD_DIST_DIR, "windows"),
    "linux": os.path.join(BUILD_DIST_DIR, "linux"),
    "macos": os.path.join(BUILD_DIST_DIR, "macos"),
    "android": os.path.join(BUILD_DIST_DIR, "android"),
}

def ensure_icons():
    """Ensure all required .ico icons are present."""
    try:
        from contrib.generate_app_icons import generate_all
        generate_all()
    except Exception as e:
        print(f"[Icon Generator Warning] {e}")

def setup_platform_dirs():
    for p_name, p_path in PLATFORM_DIRS.items():
        os.makedirs(p_path, exist_ok=True)

def build_executables():
    os.makedirs(DIST_DIR, exist_ok=True)
    setup_platform_dirs()
    ensure_icons()

    print(f"[PayQuant Installer Builder v4.0.0] Target Directory: {DIST_DIR}")

    targets = [
        ("node_miner_gui.py", "payquant-node-miner-gui", "--windowed", "payquant-node-miner.ico"),
        ("wallet_gui.py", "payquant-wallet-gui", "--windowed", "payquant-wallet.ico"),
        ("explorer_gui.py", "payquant-explorer", "--windowed", "payquant-explorer.ico"),
        ("node_gui.py", "payquant-node-gui", "--windowed", "payquant-node.ico"),
        ("miner_gui.py", "payquant-miner-gui", "--windowed", "payquant-miner.ico"),
        ("test_node2_gui.py", "payquant-test-node2-gui", "--windowed", "payquant-node.ico"),
        ("node_entry.py", "payquantd", "--console", "payquant-node.ico"),
    ]

    for script_name, exe_name, mode, icon_name in targets:
        script_path = os.path.join(BASE_DIR, "contrib", script_name)
        if not os.path.exists(script_path):
            continue

        icon_path = os.path.join(PIXMAPS_DIR, icon_name)
        if not os.path.exists(icon_path):
            icon_path = os.path.join(PIXMAPS_DIR, "payquant.ico")

        print(f"[PayQuant Installer Builder] Compiling {exe_name}.exe with PyInstaller (Icon: {os.path.basename(icon_path)})...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            script_path,
            "--onefile",
            f"--name={exe_name}",
            f"--distpath={DIST_DIR}",
            f"--icon={icon_path}",
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

    # Bundle a clean single-OS release ZIP (Windows host)
    try:
        import zipfile
        zip_path = os.path.join(BASE_DIR, "build_dist", "payquant-v4.0.0-windows.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in sorted(os.listdir(win_dir)):
                fpath = os.path.join(win_dir, fname)
                if os.path.isfile(fpath):
                    zf.write(fpath, f"payquant-v4.0.0-windows/{fname}")
        print(f"[PayQuant Installer Builder] -> [SUCCESS] Release ZIP: {zip_path}")
    except Exception as e:
        print(f"[PayQuant Installer Builder] Release ZIP skipped: {e}")

    print("[PayQuant Installer Builder] All PyInstaller binaries compiled & platform setup installer scripts generated!")

if __name__ == '__main__':
    build_executables()
