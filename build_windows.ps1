<#
.SYNOPSIS
    Builds the AI OPS Studio application for Windows 11.

.DESCRIPTION
    This script automates the build process for AI OPS Studio, including:
    1. Virtual Environment activation
    2. PyInstaller build using packaging/windows/AIOpsStudio.spec
    3. Code Signing (if certificate exists)
    4. Build verification

.NOTES
    File Name      : build_windows.ps1
    Author         : Antigravity
    Prerequisite   : Run as Administrator (for certificate access)
#>

$ErrorActionPreference = "Stop"

# 0. Check for Administrator privileges
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Script is not running as Administrator."
    Write-Warning "Code signing might fail if it requires accessing protected certificate stores."
    # We don't exit here, just warn, as building might still work without signing
}

# 1. Setup Environment
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Building AI OPS Studio (Windows 11)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot
# Define paths
$SpecFile = Join-Path $ProjectRoot "packaging\windows\AIOpsStudio.spec"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"

# Smart Venv Detection
$VenvCandidates = @("venv", ".venv")
$SelectedVenv = $null

foreach ($candidate in $VenvCandidates) {
    $VenvPath = Join-Path $ProjectRoot $candidate
    $Activate = Join-Path $VenvPath "Scripts\Activate.ps1"
    $PyInst = Join-Path $VenvPath "Scripts\pyinstaller.exe"
    
    if ((Test-Path $Activate) -and (Test-Path $PyInst)) {
        $SelectedVenv = $candidate
        $VenvActivate = $Activate
        $PyInstaller = $PyInst
        break
    }
}

# Fallback if no valid venv found (try just activate)
if (-not $SelectedVenv) {
    foreach ($candidate in $VenvCandidates) {
        $Activate = Join-Path $ProjectRoot "$candidate\Scripts\Activate.ps1"
        if (Test-Path $Activate) {
            $VenvActivate = $Activate
            # Assume global pyinstaller if not in venv
            $PyInstaller = "pyinstaller" 
            break
        }
    }
}

if (-not $VenvActivate) {
    # Default fallback
    $VenvActivate = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
    $PyInstaller = "pyinstaller"
}

Write-Host "[DEBUG] VenvActivate: $VenvActivate" -ForegroundColor Magenta
Write-Host "[DEBUG] PyInstaller: $PyInstaller" -ForegroundColor Magenta

# 2. Validation / Generation
if (-not (Test-Path $SpecFile)) {
    Write-Host "[INFO] Spec file not found. Generating new spec file..." -ForegroundColor Yellow
    
    # Ensure directory exists
    $SpecDir = Split-Path $SpecFile -Parent
    if (-not (Test-Path $SpecDir)) { New-Item -ItemType Directory -Force -Path $SpecDir | Out-Null }
    
    # Generate spec
    # Note: We run pyinstaller to generate the spec in the specific    # Generate spec
    try {
        & $PyInstaller --name "AIOpsStudio" `
            --windowed `
            --icon "../../resources/icons/icon.ico" `
            --add-data "../../src/database/schema.sql;src/database" `
            --add-data "../../resources;resources" `
            --specpath "packaging/windows" `
            --noconfirm `
            src/main.py
                    
        Write-Host "[SUCCESS] Generated spec file at $SpecFile" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to generate spec file: $_"
        exit 1
    }
}

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

# 4. Activate Virtual Environment
if (Test-Path $VenvActivate) {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
    & $VenvActivate
}
else {
    Write-Warning "Virtual environment not found at $VenvActivate. Using global python/pip."
}

# 5. Run PyInstaller
Write-Host "[INFO] Running PyInstaller..." -ForegroundColor Green
try {
    # Run build
    & $PyInstaller --noconfirm --clean $SpecFile
}
catch {
    Write-Error "PyInstaller failed. Error: $_"
    exit 1
}

# 6. Verify Build
$ExePath = Join-Path $DistDir "AIOpsStudio\AIOpsStudio.exe"
if (Test-Path $ExePath) {
    Write-Host "[SUCCESS] Build created successfully at:" -ForegroundColor Green
    Write-Host "    $ExePath" -ForegroundColor White
}
else {
    Write-Error "Build failed. Executable not found at $ExePath"
    exit 1
}

# 7. Code Signing (Optional)
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
    Write-Host "[INFO] No code signing certificate found. Attempting to create one..." -ForegroundColor Yellow
    try {
        $Cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $CertSubject -KeySpec Signature -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
        Write-Host "[SUCCESS] Created self-signed certificate: $($Cert.Thumbprint)" -ForegroundColor Green
        
        # Try signing again
        Set-AuthenticodeSignature -FilePath $ExePath -Certificate $Cert -TimestampServer "http://timestamp.digicert.com"
        Write-Host "[SUCCESS] Executable signed." -ForegroundColor Green
    }
    catch {
        Write-Warning "Could not create certificate or sign executable. Run script as Administrator."
        Write-Warning "Error: $_"
    }
}

Write-Host "`nDone." -ForegroundColor Cyan
