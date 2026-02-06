# Quick Start: Creating the Installer

Follow these steps to create the Windows installer:

## 1. Download Inno Setup
- Visit: https://jrsoftware.org/isdl.php
- Download and install Inno Setup 6 (free)

## 2. Build the Application
```powershell
.\build_windows.ps1
```
This creates `dist\BlockTracker\BlockTracker.exe`

## 3. Compile the Installer

### Option A: Using GUI (Easiest)
1. Open Inno Setup Compiler
2. File → Open → `BlockTracker.iss`
3. Build → Compile (or F9)

### Option B: Command Line
```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" BlockTracker.iss
```

## 4. Find Your Installer
The installer will be at:
`packaging\output\BlockTracker-Setup-0.1.0.exe`

## That's It!
Distribute `BlockTracker-Setup-0.1.0.exe` to users. They just double-click to install.

---

For detailed information, see [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md)
