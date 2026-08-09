[Setup]
AppName=PayQuant Node & Miner Suite
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant\NodeMiner
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\build_dist\windows
OutputBaseFilename=PayQuant-Node-Miner-Setup-v6.3.0

[Files]
Source: "payquant-node-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant Node & Miner Suite"; Filename: "{app}\payquant-node-miner-gui.exe"
Name: "{commondesktop}\PayQuant Node & Miner"; Filename: "{app}\payquant-node-miner-gui.exe"