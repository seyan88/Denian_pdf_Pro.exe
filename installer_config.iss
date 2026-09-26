[Setup]
AppName=Denian Media Pro
AppVersion=2.0.0
AppPublisher=Denian
DefaultDirName={autopf}\Denian Media Pro
DefaultGroupName=Denian Media Pro
OutputDir=Releases
OutputBaseFilename=Setup_DenianMediaPro
SetupIconFile=assets\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Denian Media Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Denian Media Pro"; Filename: "{app}\Denian Media Pro.exe"
Name: "{autodesktop}\Denian Media Pro"; Filename: "{app}\Denian Media Pro.exe"; Tasks: desktopicon
