[Setup]
; Basic application information
AppName=AI OPS Studio
AppVersion=0.1.0
AppPublisher=AI Ops Studio LLC
AppPublisherURL=https://aiopsstudio.com
AppSupportURL=https://aiopsstudio.com/support
AppUpdatesURL=https://aiopsstudio.com/updates
DefaultDirName={autopf}\AIOpsStudio
DefaultGroupName=AI OPS Studio
AllowNoIcons=yes
; Output configuration
OutputDir=packaging\output
OutputBaseFilename=AIOpsStudio-Setup-0.1.0
SetupIconFile=resources\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; License and documentation
LicenseFile=LICENSE.txt
; InfoBeforeFile=README.txt

; Privileges and compatibility
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Windows 10 and later
MinVersion=10.0

; Uninstall configuration
UninstallDisplayIcon={app}\AIOpsStudio.exe
UninstallDisplayName=AI OPS Studio

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Include the entire AIOpsStudio directory from dist
Source: "dist\AIOpsStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Include LICENSE if it exists
; Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\AI OPS Studio"; Filename: "{app}\AIOpsStudio.exe"
Name: "{group}\{cm:UninstallProgram,AI OPS Studio}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional, based on user selection)
Name: "{autodesktop}\AI OPS Studio"; Filename: "{app}\AIOpsStudio.exe"; Tasks: desktopicon

[Run]
; Option to launch the application after installation
Filename: "{app}\AIOpsStudio.exe"; Description: "{cm:LaunchProgram,AI OPS Studio}"; Flags: nowait postinstall skipifsilent

[Code]
// Create AppData directory for database on first install
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create application data directory
    AppDataDir := ExpandConstant('{localappdata}\AIOpsStudio');
    if not DirExists(AppDataDir) then
      CreateDir(AppDataDir);
  end;
end;

// Clean up AppData on uninstall (optional - ask user)
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataDir: String;
  DeleteAppData: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppDataDir := ExpandConstant('{localappdata}\AIOpsStudio');
    if DirExists(AppDataDir) then
    begin
      DeleteAppData := MsgBox('Do you want to delete your database and application data?' + #13#10 + 
                               'Choose No if you plan to reinstall or want to keep your data.', 
                               mbConfirmation, MB_YESNO);
      if DeleteAppData = IDYES then
      begin
        DelTree(AppDataDir, True, True, True);
      end;
    end;
  end;
end;
