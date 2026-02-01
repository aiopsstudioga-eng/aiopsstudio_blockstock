$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "ERROR: This script must be run as an Administrator to create/access certificates."
    Pause
    exit
}
# 1. Setup Header
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Building & Signing AIOps Inventory" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

# 2. Check for Virtual Environment [cite: 1]
$VenvPath = "$ProjectRoot\venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvPath)) {
    Write-Warning "[ERROR] Virtual environment not found in venv\"
    Write-Host "Please run: python -m venv venv"
    Write-Host "Then install dependencies: pip install -r requirements.txt"
    Pause
    exit 1
}

# 3. Activate Virtual Environment
& $VenvPath

# [cite_start]4. Check PyInstaller [cite: 2]
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "[INFO] Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# [cite_start]5. Clean Old Builds [cite: 2]
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# [cite_start]6. Run PyInstaller [cite: 2]
Write-Host "[INFO] Running PyInstaller..." -ForegroundColor Green
pyinstaller --noconfirm --clean packaging\windows\AIOpsInventory.spec

# [cite_start]7. Check Build Success [cite: 3]
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ERROR] Build failed!"
    Pause
    exit 1
}

# 8. Digital Signing
$ExePath = "dist\AIOpsInventory\AIOpsInventory.exe"
$CertSubject = "CN=AIOpsLocalDev"

Write-Host "[INFO] Checking for Code Signing Certificate..." -ForegroundColor Yellow
$Cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $CertSubject } | Select-Object -First 1

if (-not $Cert) {
    Write-Host "[INFO] Creating a new self-signed certificate..." -ForegroundColor Gray
    $Cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $CertSubject -KeySpec Signature -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
}

Write-Host "[INFO] Signing executable..." -ForegroundColor Green
Set-AuthenticodeSignature -FilePath $ExePath -Certificate $Cert -TimestampServer "http://timestamp.digicert.com"

Write-Host "`nBuild & Sign Complete!" -ForegroundColor Cyan
Pause