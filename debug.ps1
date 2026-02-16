<#
.SYNOPSIS
    Ultimate Debug Build Script for AI OPS Studio
#>

$ErrorActionPreference = "Continue" # Changed to Continue to see all errors

Write-Host "--- DIAGNOSTIC START ---" -ForegroundColor Cyan
$ProjectRoot = $PSScriptRoot
Set-Location -Path $ProjectRoot

# 1. Strict Path Verification
$PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
$MainPy = "$ProjectRoot\src\main.py"

$Paths = @{
    "Python Interpreter" = $PythonExe
    "Main Entry Point"   = $MainPy
    "Database Schema"    = "$ProjectRoot\src\database\schema.sql"
}

foreach ($name in $Paths.Keys) {
    if (Test-Path $Paths[$name]) {
        Write-Host "[OK] Found $name" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Missing $name" -ForegroundColor Red
    }
}

# 2. Verify Nuitka is actually usable
Write-Host "`n[INFO] Checking Nuitka version..." -ForegroundColor Yellow
& $PythonExe -m nuitka --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FATAL] Nuitka is not responding. Try: .\.venv\Scripts\python.exe -m pip install nuitka" -ForegroundColor Red
    pause
    exit
}

# 3. Execution with Verbose Logging
Write-Host "`n[INFO] Starting Build..." -ForegroundColor Cyan
$NuitkaArgs = @(
    "src/main.py",
    "--standalone",
    "--output-dir=dist",
    "--remove-output",
    "--enable-plugin=pyqt6",
    "--windows-console-mode=force",
    "--show-modules" # This will show us exactly which file it's working on
)

try {
    # We call it directly to capture the raw stream
    & $PythonExe -m nuitka @NuitkaArgs 2>&1 | Tee-Object -FilePath "build_log.txt"
}
catch {
    Write-Host "PowerShell Catch: $_" -ForegroundColor Red
}

Write-Host "`n--- DIAGNOSTIC END ---" -ForegroundColor Cyan
Write-Host "A full log has been saved to build_log.txt"
Read-Host "Press Enter to close"