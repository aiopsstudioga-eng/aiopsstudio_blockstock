# Automated Testing Guide

This directory contains automated tests for the logging and error handling system.

## Quick Start

### Option 1: Python Test Script (Comprehensive)

```powershell
python test_logging.py
```

**What it tests:**
- ✅ Logger initialization
- ✅ Log file creation in AppData
- ✅ All log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Exception logging with stack traces
- ✅ Log file content format
- ✅ Error handler imports

**Expected output:**
```
Results: 6/6 tests passed
🎉 All tests passed!
```

### Option 2: PowerShell Verification (Quick Check)

```powershell
.\verify_logging.ps1
```

**What it checks:**
- ✅ Log directory exists
- ✅ Log file exists
- ✅ Log format is correct (timestamps, levels, modules)
- ✅ Recent log activity
- 📋 Displays last 10 log entries

**Expected output:**
```
Passed: 4 / 4
🎉 All tests passed!
```

---

## Testing After Building .exe

After building the installer and installing the app:

### Step 1: Install the application
```powershell
.\build_windows.ps1
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AIOpsStudio.iss
# Install from packaging\output\AIOpsStudio-Setup-0.1.0-beta.exe
```

### Step 2: Run the installed app
- Launch from Start Menu

### Step 3: Verify logging works
```powershell
.\verify_logging.ps1
```

You should see logs from the installed application in:
```
C:\Users\<YourUsername>\AppData\Local\AIOpsStudio\logs\aiopsstudio.log
```

---

## Manual Error Testing

### Trigger Dashboard Error

1. Navigate to Dashboard page
2. If error occurs, you should see:
   - ✅ Error dialog appears
   - ✅ Error logged to file with stack trace

### Trigger Export Error

1. Go to Items page
2. Click "Export CSV"
3. Try to save to invalid path (e.g., `Z:\nonexistent\path.csv`)
4. Check logs for error entry

---

## Log File Location

**Development mode:**
```
C:\Users\<YourUsername>\AppData\Local\AIOpsStudio\logs\aiopsstudio.log
```

**Production (.exe):**
Same location - logs work in both modes!

---

## Troubleshooting

### No log file created
- Run the app at least once
- Check if AppData directory exists: `$env:LOCALAPPDATA\AIOpsStudio`

### Tests fail
- Ensure you've run the app at least once to create logs
- Check Python version (requires Python 3.8+)
- Verify PyQt6 is installed

### Log file empty
- Application might not have logged anything yet
- Try triggering an action (navigate to Dashboard, generate report, etc.)

---

## What Success Looks Like

✅ **Log file exists** in AppData  
✅ **Contains timestamps** and structured format  
✅ **Errors show dialogs** (not silent failures)  
✅ **Stack traces** captured for exceptions  
✅ **Works in .exe** (production mode)

---

## Next Steps

After verifying logging works:

1. ✅ Build production installer
2. ✅ Test in installed app
3. ✅ Verify error dialogs appear
4. ✅ Check log rotation (after 10MB)
5. 🚀 Deploy to users!
