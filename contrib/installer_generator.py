#!/usr/bin/env python3
"""
PayQuant (PQN) Multi-Platform Installers Generator v6.3.0

Generates platform setup installers (Windows .exe Installers, Linux AppImages, macOS DMGs, Android APKs)
for:
 1. PayQuant Node Setup Installer (Node)
 2. PayQuant Miner Setup Installer (Miner)
 3. PayQuant Node & Miner Suite Setup Installer (Node + Miner Suite)
 4. PayQuant Light Wallet Setup Installer (Wallet)
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
    iss_node = """
[Setup]
AppName=PayQuant Full Node
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\Node
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Node-Setup-v6.3.0

[Files]
Source: "payquant-node-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant Full Node"; Filename: "{app}\\payquant-node-gui.exe"
Name: "{commondesktop}\\PayQuant Full Node"; Filename: "{app}\\payquant-node-gui.exe"
    """

    iss_miner = """
[Setup]
AppName=PayQuant RinHash Solo Miner
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\Miner
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Miner-Setup-v6.3.0

[Files]
Source: "payquant-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant RinHash Solo Miner"; Filename: "{app}\\payquant-miner-gui.exe"
Name: "{commondesktop}\\PayQuant Miner"; Filename: "{app}\\payquant-miner-gui.exe"
    """

    iss_node_miner = """
[Setup]
AppName=PayQuant Node & Miner Suite
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\\PayQuant\\NodeMinerSuite
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\\build_dist\\windows
OutputBaseFilename=PayQuant-Node-Miner-Suite-Setup-v6.3.0

[Files]
Source: "payquant-node-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PayQuant Node & Miner Suite"; Filename: "{app}\\payquant-node-miner-gui.exe"
Name: "{commondesktop}\\PayQuant Node & Miner Suite"; Filename: "{app}\\payquant-node-miner-gui.exe"
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

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(os.path.join(DIST_DIR, "setup_node.iss"), "w") as f:
        f.write(iss_node.strip())
    with open(os.path.join(DIST_DIR, "setup_miner.iss"), "w") as f:
        f.write(iss_miner.strip())
    with open(os.path.join(DIST_DIR, "setup_node_miner_suite.iss"), "w") as f:
        f.write(iss_node_miner.strip())
    with open(os.path.join(DIST_DIR, "setup_wallet.iss"), "w") as f:
        f.write(iss_wallet.strip())

    print("[Installer Generator] Generated Inno Setup .iss installer scripts in dist/")

if __name__ == '__main__':
    create_inno_setup_scripts()
