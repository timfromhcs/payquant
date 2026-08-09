[Setup]
AppName=PayQuant RinHash Solo Miner
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant\Miner
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\build_dist\windows
OutputBaseFilename=PayQuant-Miner-Setup-v6.3.0

[Files]
Source: "payquant-miner-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant RinHash Solo Miner"; Filename: "{app}\payquant-miner-gui.exe"
Name: "{commondesktop}\PayQuant Miner"; Filename: "{app}\payquant-miner-gui.exe"