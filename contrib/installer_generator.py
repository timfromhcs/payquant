#!/usr/bin/env python3
"""
PayQuant (PQN) Platform Installers Generator v6.3.0

Generates platform setup installers (Windows .exe Installers, Linux AppImages, macOS DMGs, Android APKs)
for:
 1. Combined Node + Miner Suite Installer
 2. Standalone Light Wallet Installer
 3. Standalone Public Explorer Installer
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIST_DIR = os.path.join(BASE_DIR, "build_dist")

def create_inno_setup_scripts():
    """Generates Inno Setup installer scripts (.iss) for Windows setup executables"""
    iss_node_miner = """
[Setup]
AppName=PayQuant Node & Miner Suite
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\NodeMiner
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Node-Miner-Setup-v6.3.0

[Files]
Source: "payquant-node-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant Node & Miner Suite"; Filename: "{app}\\payquant-node-miner-gui.exe"
Name: "{commondesktop}\\PayQuant Node & Miner"; Filename: "{app}\\payquant-node-miner-gui.exe"
    """

    iss_wallet = """
[Setup]
AppName=PayQuant Light Wallet
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\Wallet
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Wallet-Setup-v6.3.0

[Files]
Source: "payquant-wallet-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant Light Wallet"; Filename: "{app}\\payquant-wallet-gui.exe"
Name: "{commondesktop}\\PayQuant Wallet"; Filename: "{app}\\payquant-wallet-gui.exe"
    """

    iss_explorer = """
[Setup]
AppName=PayQuant Public Explorer
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\Explorer
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Explorer-Setup-v6.3.0

[Files]
Source: "payquant-explorer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant Public Explorer"; Filename: "{app}\\payquant-explorer.exe"
Name: "{commondesktop}\\PayQuant Explorer"; Filename: "{app}\\payquant-explorer.exe"
    """

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(os.path.join(DIST_DIR, "setup_node_miner.iss"), "w") as f:
        f.write(iss_node_miner.strip())
    with open(os.path.join(DIST_DIR, "setup_wallet.iss"), "w") as f:
        f.write(iss_wallet.strip())
    with open(os.path.join(DIST_DIR, "setup_explorer.iss"), "w") as f:
        f.write(iss_explorer.strip())

    print("[Installer Generator] Generated Inno Setup .iss installer scripts in dist/")

if __name__ == '__main__':
    create_inno_setup_scripts()
