<#
.SYNOPSIS
    Builds the AI OPS Studio application for Windows using Nuitka.

.DESCRIPTION
    This script builds the application as a Windows executable using Nuitka,
    which compiles Python to optimized C code for better performance and
    code protection compared to PyInstaller.

.NOTES
    File Name      : build_nuitka.ps1
    Author         : AIOps Studio Team
    Prerequisite   : Visual Studio Build Tools with C++ workload
#>

$ErrorActionPreference = "Stop"

# 0. Check for Administrator privileges (optional, for code signing)
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Script is not running as Administrator."
    Write-Warning "Code signing will be skipped if it requires admin privileges."
}

# 1. Setup Environment
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Building AI OPS Studio with Nuitka" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

# Define paths
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"

# Virtual Environment Detection
$VenvCandidates = @(".venv", "venv")
$SelectedVenv = $null

foreach ($candidate in $VenvCandidates) {
    $VenvPath = Join-Path $ProjectRoot $candidate
    $Activate = Join-Path $VenvPath "Scripts\Activate.ps1"
    $Python = Join-Path $VenvPath "Scripts\python.exe"
    
    if ((Test-Path $Activate) -and (Test-Path $Python)) {
        $SelectedVenv = $candidate
        $VenvActivate = $Activate
        $PythonExe = $Python
        break
    }
}

if (-not $VenvActivate) {
    Write-Error "Virtual environment not found. Please create one with: python -m venv venv"
    exit 1
}

Write-Host "[INFO] Using virtual environment: $SelectedVenv" -ForegroundColor Green
Write-Host "[DEBUG] Python: $PythonExe" -ForegroundColor Magenta

# 2. Check/Install Nuitka dependencies
Write-Host "[INFO] Checking Nuitka installation..." -ForegroundColor Yellow

# Try to run nuitka to see if it's installed
$NuitkaCheck = & $PythonExe -m nuitka --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Nuitka not found. Installing..." -ForegroundColor Yellow
    & $PythonExe -m pip install nuitka
}

# Install additional Nuitka dependencies (ordered-set is included in newer Nuitka)
Write-Host "[INFO] Installing Nuitka dependencies..." -ForegroundColor Yellow
& $PythonExe -m pip install ordered-set zstandard 2>$null
Write-Host "[INFO] Note: Nuitka 4.0+ includes colorama support natively" -ForegroundColor Yellow

Write-Host "[SUCCESS] Nuitka installed: $(& $PythonExe -m nuitka --version)" -ForegroundColor Green

# 3. Clean previous builds
Write-Host "[INFO] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DistDir) { 
    try {
        Remove-Item -Path $DistDir -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Could not fully clean dist directory (files may be in use). Proceeding anyway..."
    }
}
if (Test-Path $BuildDir) { 
    try {
        Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Could not fully clean build directory. Proceeding anyway..."
    }
}

# 4. Run Nuitka Build
Write-Host "[INFO] Running Nuitka build..." -ForegroundColor Green

# Build command with all necessary options
$NuitkaArgs = @(
    # Main entry point
    "src/main.py",
    
    # Standalone mode (folder with exe + DLLs, avoids AV false positives)
    "--standalone",
    
    # Output filename (name the exe after the product, not the script)
    "--output-filename=AIOpsStudio.exe",
    
    # Output directory
    "--output-dir=$DistDir",
    
    # Application name (product name for Windows)
    "--product-name=AIOpsStudio",
    "--company-name=AIOps Studio",
    "--product-version=1.0.0",
    "--file-version=1.0.0.0",
    
    # Console mode forced for debugging
    "--windows-console-mode=force",
    
    # Icon
    "--windows-icon-from-ico=resources/icons/icon.ico",
    
    # Include data files
    "--include-data-file=src/database/schema.sql=src/database/schema.sql",
    "--include-data-dir=resources=resources",
    
    # PyQt6 plugin
    "--enable-plugin=pyqt6",
    
    # Remove output directory before building
    "--remove-output",
    
    # Assume yes for downloads (Nuitka may download missing stuff)
    "--assume-yes-for-downloads",
    
    # Show progress (nuitka 4.0+ uses --progress-bar)
    "--progress-bar=auto",
    
    # Follow imports to ensure all dependencies are included
    "--follow-imports",
    
    # Include some common modules that might be missed
    "--include-module=reportlab",
    "--include-module=pandas",
    "--include-module=openpyxl",
    "--include-module=matplotlib",
    
    # LTO (Link Time Optimization) for better performance
    "--lto=yes"
)

# Run Nuitka
& $PythonExe -m nuitka @NuitkaArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Nuitka build failed with exit code: $LASTEXITCODE"
    exit 1
}

# 5. Verify Build - Standalone output goes to main.dist/ folder
$StandaloneDir = Join-Path $DistDir "main.dist"
$ExePath = Join-Path $StandaloneDir "AIOpsStudio.exe"
if (Test-Path $ExePath) {
    $FolderSize = (Get-ChildItem $StandaloneDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "[SUCCESS] Build created successfully!" -ForegroundColor Green
    Write-Host "    Executable: $ExePath" -ForegroundColor White
    Write-Host "    Folder size: $([math]::Round($FolderSize, 2)) MB" -ForegroundColor White
    Write-Host "    Tip: Package this folder with Inno Setup (AIOpsStudio.iss) for distribution." -ForegroundColor Yellow
}
else {
    Write-Error "Build failed. Executable not found at $ExePath"
    exit 1
}

# 6. Code Signing (Optional)
$CertSubject = "CN=AIOpsLocalDev"
$Cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $CertSubject } | Select-Object -First 1

if ($Cert) {
    Write-Host "[INFO] Found development certificate. Signing executable..." -ForegroundColor Green
    try {
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $Cert -TimestampServer "http://timestamp.digicert.com"
        Write-Host "[SUCCESS] Executable signed." -ForegroundColor Green
    }
    catch {
        Write-Warning "Signing failed: $_"
    }
}
else {
    Write-Host "[INFO] No code signing certificate found. Skipping signing." -ForegroundColor Yellow
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "              Build Complete!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Output folder: $StandaloneDir" -ForegroundColor White
Write-Host "Executable:    $ExePath" -ForegroundColor White
Write-Host ""
