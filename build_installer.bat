@echo off
echo Starting Build Process for AI OPS Studio...

:: 1. Force the script to start in your exact project root
cd /d "D:\Dev\GitHub\aiopsstudio_blockstock\aiopsstudio_blockstock"

:: 2. Activate the virtual environment
call venv\Scripts\activate

:: ---------------------------------------------------------
:: CRITICAL STEP: Install Libraries BEFORE Building
:: ---------------------------------------------------------
if exist "requirements.txt" (
    echo [INFO] Installing/Updating dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found! 
    echo Please run: pip install pandas numpy pyqt6 (or whatever libraries you use)
    pause
)

:: 3. Run PyInstaller (pointing exactly to your spec file location)
echo Running PyInstaller...
python -m PyInstaller --noconfirm "packaging\windows\AIOpsStudio.spec"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b %ERRORLEVEL%
)

:: 4. Run Inno Setup Compiler (pointing to your local AppData install)
echo Compiling Installer...
"C:\Users\miker\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "AIOpsStudio.iss"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Inno Setup compilation failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Success! Your installer is in packaging\output\
pause