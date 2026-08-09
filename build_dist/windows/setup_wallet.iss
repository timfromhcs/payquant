[Setup]
AppName=PayQuant Light Wallet
AppVersion=4.0.0
WizardStyle=modern
DefaultDirName={autopf}\PayQuant\Wallet
DefaultGroupName=PayQuant Ecosystem
Compression=lzma2
SolidCompression=yes
OutputDir=..\build_dist\windows
OutputBaseFilename=PayQuant-Wallet-Setup-v4.0.0

[Files]
Source: "payquant-wallet-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PayQuant Light Wallet"; Filename: "{app}\payquant-wallet-gui.exe"
Name: "{commondesktop}\PayQuant Wallet"; Filename: "{app}\payquant-wallet-gui.exe"