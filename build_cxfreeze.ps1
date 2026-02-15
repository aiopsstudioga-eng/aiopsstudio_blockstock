<#
.SYNOPSIS
    Builds the AI OPS Studio application for Windows using cx_Freeze.

.DESCRIPTION
    This script automates the build process for AI OPS Studio using cx_Freeze:
    1. Virtual Environment activation
    2. Clean previous builds
    3. Run cx_Freeze build
    4. Verify build output

.NOTES
    File Name      : build_cxfreeze.ps1
    Prerequisite   : cx_Freeze installed (pip install cx_Freeze)
#>

$ErrorActionPreference = "Stop"

# 0. Setup
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Building AI OPS Studio (cx_Freeze)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

# Define paths
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"

# 1. Smart Venv Detection
$VenvCandidates = @("venv", ".venv")
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

if (-not $PythonExe) {
    # Fallback to global python
    $PythonExe = "python"
}

Write-Host "[DEBUG] Python: $PythonExe" -ForegroundColor Magenta

# 2. Check for cx_Freeze
Write-Host "[INFO] Checking for cx_Freeze..." -ForegroundColor Yellow
try {
    & $PythonExe -c "import cx_Freeze" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] cx_Freeze not found. Installing..." -ForegroundColor Yellow
        & $PythonExe -m pip install cx_Freeze
    }
}
catch {
    Write-Host "[INFO] cx_Freeze not found. Installing..." -ForegroundColor Yellow
    & $PythonExe -m pip install cx_Freeze
}

# 3. Clean previous builds
Write-Host "[INFO] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DistDir) { 
    try {
        Remove-Item -Path $DistDir -Recurse -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "Could not fully clean dist directory. Proceeding anyway..."
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

# 4. Activate Virtual Environment (optional but recommended)
if (Test-Path $VenvActivate) {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
    & $VenvActivate
}

# 5. Run cx_Freeze Build
Write-Host "[INFO] Running cx_Freeze build..." -ForegroundColor Green
try {
    & $PythonExe setup.py build
}
catch {
    Write-Error "cx_Freeze build failed. Error: $_"
    exit 1
}

# 6. Verify Build
$ExePath = Join-Path $DistDir "AIOpsStudio.exe"
if (Test-Path $ExePath) {
    Write-Host "[SUCCESS] Build created successfully at:" -ForegroundColor Green
    Write-Host "    $ExePath" -ForegroundColor White
    
    # Get file size
    $FileSize = (Get-Item $ExePath).Length / 1MB
    Write-Host "    Size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor White
}
else {
    # Check in subdirectory
    $AltExePath = Get-ChildItem -Path $DistDir -Filter "*.exe" -Recurse | Select-Object -First 1
    if ($AltExePath) {
        Write-Host "[SUCCESS] Build created successfully at:" -ForegroundColor Green
        Write-Host "    $($AltExePath.FullName)" -ForegroundColor White
    }
    else {
        Write-Error "Build failed. Executable not found."
        exit 1
    }
}

Write-Host "`nDone." -ForegroundColor Cyan
Write-Host "To run the application, execute: $ExePath" -ForegroundColor Yellow
