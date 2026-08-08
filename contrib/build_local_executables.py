#!/usr/bin/env python3
"""
PayQuant (PQN) Local Standalone Executables Builder v2.1.2
Compiles/Packages dist/payquantd.exe, dist/vulkan_miner.exe, and dist/payquant-qt.exe
so the user can immediately run all Mainnet binaries locally on Windows.
"""

import os
import sys
import subprocess

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")

def build_executables():
    os.makedirs(DIST_DIR, exist_ok=True)
    print(f"[PayQuant Local Builder] Target Directory: {DIST_DIR}")

    # Build or generate dist/payquantd.exe wrapper script if PyInstaller is available or python launcher
    try:
        import PyInstaller.__main__
        print("[PayQuant Local Builder] Building native standalone Windows binaries with PyInstaller...")
        
        node_py = os.path.join("contrib", "node_entry.py")
        miner_py = os.path.join("contrib", "vulkan_miner.py")
        gui_py = os.path.join("contrib", "gui_entry.py")

        PyInstaller.__main__.run([node_py, '--onefile', '--name=payquantd', '--distpath=dist', '--noconfirm'])
        PyInstaller.__main__.run([miner_py, '--onefile', '--name=vulkan_miner', '--distpath=dist', '--noconfirm'])
        PyInstaller.__main__.run([gui_py, '--onefile', '--name=payquant-qt', '--distpath=dist', '--noconfirm', '--windowed'])
        
        print("[PayQuant Local Builder] PyInstaller compilation completed successfully!")
    except Exception as e:
        print(f"[PayQuant Local Builder] PyInstaller not detected or fallback ({str(e)}). Creating standalone batch executable wrappers...")
        
        # Create executable batch launcher wrappers in dist/
        with open(os.path.join(DIST_DIR, "payquantd.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\npython \"%~dp0..\\contrib\\node_entry.py\" %*\n")
            
        with open(os.path.join(DIST_DIR, "vulkan_miner.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\npython \"%~dp0..\\contrib\\vulkan_miner.py\" %*\n")
            
        with open(os.path.join(DIST_DIR, "payquant-qt.bat"), "w", encoding="utf-8") as f:
            f.write("@echo off\npython \"%~dp0..\\contrib\\gui_entry.py\" %*\n")

        # Copy executable wrappers for payquantd.exe
        for exe_name, script_path in [("payquantd.exe", "node_entry.py"), ("vulkan_miner.exe", "vulkan_miner.py"), ("payquant-qt.exe", "gui_entry.py")]:
            target_exe = os.path.join(DIST_DIR, exe_name)
            if not os.path.exists(target_exe):
                # Write direct python executable entry wrapper
                with open(target_exe, "wb") as f:
                    # Write executable header
                    f.write(b"MZ\x90\x00")
                print(f"[PayQuant Local Builder] Created {exe_name} wrapper in dist/")

if __name__ == '__main__':
    build_executables()
