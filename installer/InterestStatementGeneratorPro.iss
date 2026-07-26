#define MyAppName "Interest Statement Generator Pro"
#define MyAppVersion "0.9.0-beta"
#define MyAppPublisher "Interest Statement Generator Pro"
#define MyAppExeName "InterestStatementGeneratorPro.exe"

[Setup]
AppId={{A0ED714E-7077-4D07-81ED-D0D1A7604B1F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Interest Statement Generator Pro
DefaultGroupName={#MyAppName}
OutputDir=..\dist\installer
OutputBaseFilename=InterestStatementGeneratorPro-v0.9.0-beta-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\dist\InterestStatementGeneratorPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
