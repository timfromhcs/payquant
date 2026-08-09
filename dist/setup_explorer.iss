[Setup]
AppName=PayQuant Public Explorer
AppVersion=6.3.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant\Explorer
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\build_dist\windows
OutputBaseFilename=PayQuant-Explorer-Setup-v6.3.0

[Files]
Source: "payquant-explorer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant Public Explorer"; Filename: "{app}\payquant-explorer.exe"
Name: "{commondesktop}\PayQuant Explorer"; Filename: "{app}\payquant-explorer.exe"