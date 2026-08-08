#!/usr/bin/env python3
"""
PayQuant (PQN) Local Standalone Executables Builder v3.0.0
Compiles/Packages dist/payquant-node-gui.exe, dist/payquant-miner-gui.exe, dist/payquantd.exe, and dist/payquant-qt.exe
so users can run native standalone Node, Miner, and Wallet binaries on Windows, Linux, and macOS.
"""

import os
import sys
import subprocess

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")

def build_executables():
    os.makedirs(DIST_DIR, exist_ok=True)
    print(f"[PayQuant Standalone Builder] Target Directory: {DIST_DIR}")

    try:
        import PyInstaller.__main__
        print("[PayQuant Standalone Builder] Compiling native standalone executables with PyInstaller...")

        node_gui_py = os.path.join("contrib", "node_gui.py")
        miner_gui_py = os.path.join("contrib", "miner_gui.py")
        node_py = os.path.join("contrib", "node_entry.py")
        gui_py = os.path.join("contrib", "gui_entry.py")

        PyInstaller.__main__.run([node_gui_py, '--onefile', '--name=payquant-node-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([miner_gui_py, '--onefile', '--name=payquant-miner-gui', '--distpath=dist', '--noconfirm', '--windowed'])
        PyInstaller.__main__.run([node_py, '--onefile', '--name=payquantd', '--distpath=dist', '--noconfirm'])
        PyInstaller.__main__.run([gui_py, '--onefile', '--name=payquant-qt', '--distpath=dist', '--noconfirm', '--windowed'])

        print("[PayQuant Standalone Builder] All PyInstaller standalone binaries compiled successfully!")

    except Exception as e:
        print(f"[PayQuant Standalone Builder] Fallback script generation ({str(e)})...")
        with open(os.path.join(DIST_DIR, "payquant-node-gui.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\npython \"%~dp0..\\contrib\\node_gui.py\" %*\n")

        with open(os.path.join(DIST_DIR, "payquant-miner-gui.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\npython \"%~dp0..\\contrib\\miner_gui.py\" %*\n")

if __name__ == '__main__':
    build_executables()
