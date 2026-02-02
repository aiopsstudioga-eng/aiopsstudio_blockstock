<#
.SYNOPSIS
    Builds the BlockTracker application for Windows 11.

.DESCRIPTION
    This script automates the build process for BlockTracker, including:
    1. Virtual Environment activation
    2. PyInstaller build using packaging/windows/BlockTracker.spec
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
Write-Host "      Building BlockTracker (Windows 11)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot
Write-Host "[INFO] Project Root: $ProjectRoot" -ForegroundColor Gray

# Define paths
$SpecFile = Join-Path $ProjectRoot "packaging\windows\BlockTracker.spec"
$VenvActivate = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"

# 2. Validation
if (-not (Test-Path $SpecFile)) {
    Write-Error "Spec file not found at: $SpecFile"
    exit 1
}

# 3. Clean previous builds
Write-Host "[INFO] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DistDir) { Remove-Item -Path $DistDir -Recurse -Force }
if (Test-Path $BuildDir) { Remove-Item -Path $BuildDir -Recurse -Force }

# 4. Activate Virtual Environment
if (Test-Path $VenvActivate) {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
    & $VenvActivate
} else {
    Write-Warning "Virtual environment not found at $VenvActivate. Using global python/pip."
}

# 5. Run PyInstaller
Write-Host "[INFO] Running PyInstaller..." -ForegroundColor Green
try {
    # Check if pyinstaller is installed
    pyinstaller --version | Out-Null
    
    # Run build
    pyinstaller --noconfirm --clean $SpecFile
} catch {
    Write-Error "PyInstaller failed. Error: $_"
    exit 1
}

# 6. Verify Build
$ExePath = Join-Path $DistDir "BlockTracker\BlockTracker.exe"
if (Test-Path $ExePath) {
    Write-Host "[SUCCESS] Build created successfully at:" -ForegroundColor Green
    Write-Host "    $ExePath" -ForegroundColor White
} else {
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
    } catch {
        Write-Warning "Signing failed: $_"
    }
} else {
    Write-Host "[INFO] No code signing certificate found (Subject: $CertSubject). Skipping signing." -ForegroundColor Yellow
}

Write-Host "`nDone." -ForegroundColor Cyan
