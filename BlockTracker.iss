[Setup]
; Basic application information
AppName=BlockTracker
AppVersion=0.1.0
AppPublisher=AI Ops Studio LLC
AppPublisherURL=https://aiopsstudio.com
AppSupportURL=https://aiopsstudio.com/support
AppUpdatesURL=https://aiopsstudio.com/updates
DefaultDirName={autopf}\BlockTracker
DefaultGroupName=BlockTracker
AllowNoIcons=yes
; Output configuration
OutputDir=packaging\output
OutputBaseFilename=BlockTracker-Setup-0.1.0
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
UninstallDisplayIcon={app}\BlockTracker.exe
UninstallDisplayName=BlockTracker

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Include the entire BlockTracker directory from dist
Source: "dist\BlockTracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Include LICENSE if it exists
; Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\BlockTracker"; Filename: "{app}\BlockTracker.exe"
Name: "{group}\{cm:UninstallProgram,BlockTracker}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional, based on user selection)
Name: "{autodesktop}\BlockTracker"; Filename: "{app}\BlockTracker.exe"; Tasks: desktopicon

[Run]
; Option to launch the application after installation
Filename: "{app}\BlockTracker.exe"; Description: "{cm:LaunchProgram,BlockTracker}"; Flags: nowait postinstall skipifsilent

[Code]
// Create AppData directory for database on first install
procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create application data directory
    AppDataDir := ExpandConstant('{localappdata}\BlockTracker');
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
    AppDataDir := ExpandConstant('{localappdata}\BlockTracker');
    if DirExists(AppDataDir) then
    begin
      DeleteAppData := MsgBox('Do you want to delete your inventory database and application data?' + #13#10 + 
                               'Choose No if you plan to reinstall or want to keep your data.', 
                               mbConfirmation, MB_YESNO);
      if DeleteAppData = IDYES then
      begin
        DelTree(AppDataDir, True, True, True);
      end;
    end;
  end;
end;
