@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Building AIOps Inventory for Windows 11
echo ========================================================

:: Ensure we are in the project root
cd /d "%~dp0"

echo Project Root: %CD%

:: Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in venv\
    echo Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install PyInstaller if missing
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Run PyInstaller
echo [INFO] Running PyInstaller...
pyinstaller --noconfirm --clean packaging\windows\AIOpsInventory.spec

if %errorlevel% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   Build Complete!
echo ========================================================
echo.
echo App location: dist\AIOpsInventory\AIOpsInventory.exe
echo.
pause
