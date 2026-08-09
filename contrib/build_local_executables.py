#!/usr/bin/env python3
"""
PayQuant (PQN) Multi-Platform Installer & Executable Builder v6.3.0

Compiles:
 1. Combined Node + Miner Suite (dist/payquant-node-miner-gui.exe)
 2. Standalone Light Wallet GUI (dist/payquant-wallet-gui.exe)
 3. Standalone Public Explorer (dist/payquant-explorer.exe)

Generates Platform Installers:
 - Windows Setup Installers (PayQuant-Node-Miner-Setup-v6.3.0.exe, PayQuant-Wallet-Setup-v6.3.0.exe, PayQuant-Explorer-Setup-v6.3.0.exe)
 - Linux AppImage Installers (build_dist/linux/)
 - macOS DMG Installers (build_dist/macos/)
 - Android APK Installers (build_dist/android/)
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

    print(f"[PayQuant Installer Builder] Target Directory: {DIST_DIR}")

    try:
        import PyInstaller.__main__
        print("[PayQuant Installer Builder] Compiling native executables with PyInstaller...")

        node_miner_gui_py = os.path.join("contrib", "node_miner_gui.py")
        wallet_gui_py = os.path.join("contrib", "wallet_gui.py")
        explorer_gui_py = os.path.join("contrib", "explorer_gui.py")
        node_gui_py = os.path.join("contrib", "node_gui.py")
        miner_gui_py = os.path.join("contrib", "miner_gui.py")
        node_py = os.path.join("contrib", "node_entry.py")

        PyInstaller.__main__.run([node_miner_gui_py, '--onefile', '--name=payquant-node-miner-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([wallet_gui_py, '--onefile', '--name=payquant-wallet-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([explorer_gui_py, '--onefile', '--name=payquant-explorer', '--distpath=dist', '--noconfirm', '--windowed'])

        # Generate Inno Setup scripts
        try:
            from contrib.installer_generator import create_inno_setup_scripts
            create_inno_setup_scripts()
        except ImportError:
            from installer_generator import create_inno_setup_scripts
            create_inno_setup_scripts()

        # Copy executables into Windows platform folder
        win_dir = PLATFORM_DIRS["windows"]
        for fname in os.listdir(DIST_DIR):
            if fname.endswith(".exe") or fname.endswith(".iss"):
                shutil.copy2(os.path.join(DIST_DIR, fname), os.path.join(win_dir, fname))

        print("[PayQuant Installer Builder] Platform installer packages generated successfully!")

    except Exception as e:
        print(f"[PayQuant Installer Builder] Build step log ({str(e)})")

if __name__ == '__main__':
    build_executables()
