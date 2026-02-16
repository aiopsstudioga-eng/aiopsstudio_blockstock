# Automated Logging Verification Script
# Tests that logging system is working correctly

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "LOGGING SYSTEM VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$logPath = "$env:LOCALAPPDATA\AIOpsStudio\logs\aiopsstudio.log"
$testsPassed = 0
$totalTests = 0

# Test 1: Check if log directory exists
$totalTests++
Write-Host "Test 1: Log Directory Exists" -ForegroundColor Yellow
$logDir = Split-Path $logPath -Parent
if (Test-Path $logDir) {
    Write-Host "  ✅ PASS: Log directory exists" -ForegroundColor Green
    Write-Host "     Location: $logDir" -ForegroundColor Gray
    $testsPassed++
}
else {
    Write-Host "  ❌ FAIL: Log directory not found" -ForegroundColor Red
}

# Test 2: Check if log file exists
$totalTests++
Write-Host "`nTest 2: Log File Exists" -ForegroundColor Yellow
if (Test-Path $logPath) {
    Write-Host "  ✅ PASS: Log file exists" -ForegroundColor Green
    $fileInfo = Get-Item $logPath
    Write-Host "     Size: $($fileInfo.Length) bytes" -ForegroundColor Gray
    Write-Host "     Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
    $testsPassed++
}
else {
    Write-Host "  ❌ FAIL: Log file not found" -ForegroundColor Red
    Write-Host "     Expected: $logPath" -ForegroundColor Gray
}

# Test 3: Check log file content
if (Test-Path $logPath) {
    $totalTests++
    Write-Host "`nTest 3: Log File Content" -ForegroundColor Yellow
    
    $content = Get-Content $logPath -Raw
    $lines = Get-Content $logPath
    
    $hasTimestamps = $content -match '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    $hasLogLevels = $content -match '(INFO|WARNING|ERROR|CRITICAL|DEBUG)'
    $hasModuleNames = $content -match ' - \w+ - '
    $hasLineNumbers = $content -match ':\d+ - '
    
    if ($hasTimestamps -and $hasLogLevels -and $hasModuleNames) {
        Write-Host "  ✅ PASS: Log format is correct" -ForegroundColor Green
        Write-Host "     ✓ Timestamps found" -ForegroundColor Gray
        Write-Host "     ✓ Log levels found" -ForegroundColor Gray
        Write-Host "     ✓ Module names found" -ForegroundColor Gray
        if ($hasLineNumbers) {
            Write-Host "     ✓ Line numbers found" -ForegroundColor Gray
        }
        $testsPassed++
    }
    else {
        Write-Host "  ❌ FAIL: Log format issues" -ForegroundColor Red
        if (-not $hasTimestamps) { Write-Host "     ✗ No timestamps" -ForegroundColor Gray }
        if (-not $hasLogLevels) { Write-Host "     ✗ No log levels" -ForegroundColor Gray }
        if (-not $hasModuleNames) { Write-Host "     ✗ No module names" -ForegroundColor Gray }
    }
    
    # Test 4: Check for recent activity
    $totalTests++
    Write-Host "`nTest 4: Recent Log Activity" -ForegroundColor Yellow
    $fileInfo = Get-Item $logPath
    $timeSinceModified = (Get-Date) - $fileInfo.LastWriteTime
    
    if ($timeSinceModified.TotalMinutes -lt 60) {
        Write-Host "  ✅ PASS: Log file recently updated" -ForegroundColor Green
        Write-Host "     Last modified: $($timeSinceModified.TotalMinutes.ToString('F1')) minutes ago" -ForegroundColor Gray
        $testsPassed++
    }
    else {
        Write-Host "  ⚠️  WARNING: Log file not recently updated" -ForegroundColor Yellow
        Write-Host "     Last modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
    }
    
    # Display last 10 log entries
    Write-Host "`n----------------------------------------" -ForegroundColor Cyan
    Write-Host "Last 10 Log Entries:" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Cyan
    $lines | Select-Object -Last 10 | ForEach-Object {
        if ($_ -match 'ERROR|CRITICAL') {
            Write-Host $_ -ForegroundColor Red
        }
        elseif ($_ -match 'WARNING') {
            Write-Host $_ -ForegroundColor Yellow
        }
        elseif ($_ -match 'INFO') {
            Write-Host $_ -ForegroundColor White
        }
        else {
            Write-Host $_ -ForegroundColor Gray
        }
    }
    Write-Host "----------------------------------------`n" -ForegroundColor Cyan
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed / $totalTests" -ForegroundColor $(if ($testsPassed -eq $totalTests) { "Green" } else { "Yellow" })

if ($testsPassed -eq $totalTests) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    Write-Host "`nLog file location:" -ForegroundColor Cyan
    Write-Host "  $logPath" -ForegroundColor White
    exit 0
}
else {
    Write-Host "`n⚠️  Some tests failed" -ForegroundColor Yellow
    exit 1
}
