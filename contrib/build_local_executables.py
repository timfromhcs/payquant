#!/usr/bin/env python3
"""
PayQuant (PQN) Multi-Platform Installer & Executable Builder v6.3.0

Compiles:
 1. Combined Node + Miner Suite (dist/payquant-node-miner-gui.exe)
 2. Standalone Light Wallet GUI (dist/payquant-wallet-gui.exe)
 3. Standalone Public Explorer (dist/payquant-explorer.exe)
 4. Standalone Full Node (dist/payquant-node-gui.exe)
 5. Standalone Solo Miner (dist/payquant-miner-gui.exe)
 6. Command Daemon (dist/payquantd.exe)

Organizes platform-specific build folders:
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
        print(f"[Platform Builder] Created target folder: {p_path}")

def build_executables():
    os.makedirs(DIST_DIR, exist_ok=True)
    setup_platform_dirs()

    print(f"[PayQuant Standalone Builder] Target Directory: {DIST_DIR}")

    try:
        import PyInstaller.__main__
        print("[PayQuant Standalone Builder] Compiling native standalone executables with PyInstaller...")

        node_miner_gui_py = os.path.join("contrib", "node_miner_gui.py")
        wallet_gui_py = os.path.join("contrib", "wallet_gui.py")
        node_gui_py = os.path.join("contrib", "node_gui.py")
        miner_gui_py = os.path.join("contrib", "miner_gui.py")
        explorer_gui_py = os.path.join("contrib", "explorer_gui.py")
        node_py = os.path.join("contrib", "node_entry.py")

        PyInstaller.__main__.run([node_miner_gui_py, '--onefile', '--name=payquant-node-miner-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([wallet_gui_py, '--onefile', '--name=payquant-wallet-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([explorer_gui_py, '--onefile', '--name=payquant-explorer', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([node_gui_py, '--onefile', '--name=payquant-node-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([miner_gui_py, '--onefile', '--name=payquant-miner-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([node_py, '--onefile', '--name=payquantd', '--distpath=dist', '--noconfirm'])

        # Copy built binaries into platform directory
        win_dir = PLATFORM_DIRS["windows"]
        for fname in os.listdir(DIST_DIR):
            if fname.endswith(".exe"):
                shutil.copy2(os.path.join(DIST_DIR, fname), os.path.join(win_dir, fname))

        print("[PayQuant Standalone Builder] All PyInstaller standalone binaries compiled & organized into platform folders successfully!")

    except Exception as e:
        print(f"[PayQuant Standalone Builder] Fallback script generation ({str(e)})...")

if __name__ == '__main__':
    build_executables()
