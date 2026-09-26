[Setup]
AppName=Denian pdf Pro
AppVersion=1.0
DefaultDirName={autopf}\Denian pdf Pro
DefaultGroupName=Denian pdf Pro
OutputDir=Output
OutputBaseFilename=DenianPdfPro_Installer
SetupIconFile=assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Denian pdf Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Denian pdf Pro"; Filename: "{app}\Denian pdf Pro.exe"
Name: "{autodesktop}\Denian pdf Pro"; Filename: "{app}\Denian pdf Pro.exe"; Tasks: desktopicon
