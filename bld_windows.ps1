$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "ERROR: This script must be run as an Administrator to create/access certificates."
    Pause
    exit
}
# ... (Keep Admin check at the top)

# 1. Setup Header
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Building & Signing BlockStock (AIOps Inventory)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Explicitly set the location to where the script is
$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

Write-Host "[INFO] Current Directory: $ProjectRoot" -ForegroundColor Gray

# --- NEW DIAGNOSTIC STEP ---
if (-not (Test-Path "AIOpsInventory.spec")) {
    Write-Warning "[ERROR] AIOpsInventory.spec not found in $ProjectRoot"
    Write-Host "Files currently in this folder:"
    Get-ChildItem -Name
    Pause
    exit 1
}

# 2. Activate Virtual Environment
$VenvPath = "$ProjectRoot\venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    & $VenvPath
}

# 3. Run PyInstaller
Write-Host "[INFO] Running PyInstaller..." -ForegroundColor Green
# Use .\ to be explicit about the local path
pyinstaller --noconfirm --clean ".\AIOpsInventory.spec"

# 4. Check Build Success
if ($LASTEXITCODE -ne 0) {
    Write-Error "[ERROR] Build failed!"
    Pause
    exit 1
}

# 5. Digital Signing
$ExePath = "dist\BlockStock\BlockStock.exe"
$CertSubject = "CN=AIOpsLocalDev"

if (Test-Path $ExePath) {
    $Cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $CertSubject } | Select-Object -First 1
    if (-not $Cert) {
        $Cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject $CertSubject -KeySpec Signature -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
    }
    Write-Host "[INFO] Signing executable..." -ForegroundColor Green
    Set-AuthenticodeSignature -FilePath $ExePath -Certificate $Cert -TimestampServer "http://timestamp.digicert.com"
} else {
    Write-Error "[ERROR] Could not find BlockStock.exe at $ExePath"
}

Write-Host "`nBuild & Sign Complete!" -ForegroundColor Cyan
Pause