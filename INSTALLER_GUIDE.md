# Inno Setup Installer Guide

## Overview
This guide explains how to create a professional Windows installer for AIOpsStudio using Inno Setup.

## Prerequisites

### 1. Download and Install Inno Setup
1. Download from: https://jrsoftware.org/isdl.php
2. Install Inno Setup (version 6.0 or later recommended)

### 2. Build the Application First
Before creating the installer, you must build the Windows executable:
```powershell
.\build_windows.ps1
```
This creates `dist\AIOpsStudio\AIOpsStudio.exe` and all dependencies.

## Creating the Installer

### Method 1: Using Inno Setup Compiler GUI
1. Open Inno Setup Compiler
2. Click **File → Open**
3. Navigate to and open `AIOpsStudio.iss`
4. Click **Build → Compile** (or press F9)
5. The installer will be created in `packaging\output\AIOpsStudio-Setup-0.1.0.exe`

### Method 2: Command Line (Automated)
```powershell
# Compile from command line
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AIOpsStudio.iss
```

## Installer Features

The created installer includes:
- ✅ Installation to Program Files
- ✅ Start Menu shortcut
- ✅ Optional Desktop shortcut
- ✅ Automatic AppData directory creation
- ✅ Professional uninstaller
- ✅ Option to preserve data on uninstall
- ✅ Modern wizard UI

## Distribution

After compilation, distribute:
- **File**: `packaging\output\AIOpsStudio-Setup-0.1.0.exe`
- **Size**: Approximately 30-50 MB (contains full application)

Users simply:
1. Download `AIOpsStudio-Setup-0.1.0.exe`
2. Double-click to install
3. Follow the installation wizard
4. Launch from Start Menu or Desktop

## Updating the Version

When releasing a new version:
1. Update version in `AIOpsStudio.iss` (line: `AppVersion=0.1.0`)
2. Update `OutputBaseFilename` to match version
3. Rebuild the application: `.\build_windows.ps1`
4. Recompile the installer

## Optional: Creating a LICENSE.txt

The installer script references `LICENSE.txt`. Create one if needed:
```powershell
# Create a basic MIT license (example)
echo "MIT License..." > LICENSE.txt
```

## Troubleshooting

### "Source file not found" error
- Make sure you've run `.\build_windows.ps1` first
- Check that `dist\AIOpsStudio\AIOpsStudio.exe` exists

### Icon file missing
- The script references `resources\icon.ico`
- Either create this icon or comment out the `SetupIconFile` line

### Permission errors during installation
- The installer uses `PrivilegesRequired=lowest` (no admin required)
- Installation goes to user's AppData if Program Files requires admin
