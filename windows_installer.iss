; PayQuant (PQN) Windows Inno Setup Script v6.3.0
; Packages Node+Miner Suite, Standalone Wallet, and Explorer

[Setup]
AppName=PayQuant Ecosystem Suite
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=build_dist\windows
OutputBaseFilename=payquant-ecosystem-windows-setup

[Files]
Source: "dist\payquant-node-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\payquant-wallet-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\payquant-explorer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\payquantd.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant Node & Miner Suite"; Filename: "{app}\payquant-node-miner-gui.exe"
Name: "{group}\PayQuant Light Wallet"; Filename: "{app}\payquant-wallet-gui.exe"
Name: "{group}\PayQuant Public Explorer"; Filename: "{app}\payquant-explorer.exe"
Name: "{commondesktop}\PayQuant Node & Miner"; Filename: "{app}\payquant-node-miner-gui.exe"
Name: "{commondesktop}\PayQuant Wallet"; Filename: "{app}\payquant-wallet-gui.exe"
