[Setup]
AppName=PayQuant Full Node
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant\Node
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\build_dist\windows
OutputBaseFilename=PayQuant-Node-Setup-v6.3.0

[Files]
Source: "payquant-node-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant Full Node"; Filename: "{app}\payquant-node-gui.exe"
Name: "{commondesktop}\PayQuant Full Node"; Filename: "{app}\payquant-node-gui.exe"