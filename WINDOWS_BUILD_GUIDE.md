# Windows 11 Build Instructions

Since this project was developed on macOS, you will need to transfer the source code to your Windows 11 machine to build the native executable.

## 1. Prerequisites

On your Windows 11 machine, ensure you have:
- **Python 3.14+** installed (Check with `python --version` in Command Prompt)
  - *Note: Ensure "Add Python to PATH" is checked during installation*
- **Git** installed (optional, but recommended for cloning)

## 2. Transfer Source Code

You can either:
- Clone the repository directly on Windows:
  ```cmd
  git clone <your-repo-url>
  cd AIOpsSoftware
  ```
- OR copy the entire project folder from your Mac to Windows via USB/Network.

## 3. Setup Environment

Open **Command Prompt** (cmd.exe) or **PowerShell** in the project folder and run:

```cmd
:: 1. Create virtual environment
python -m venv venv

:: 2. Activate it
venv\Scripts\activate

:: 3. Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

## 4. Build the Application

We have included a one-click build script for Windows.

1. Double-click `build_windows.bat` in the project folder.
2. OR run it from the command line:
   ```cmd
   build_windows.bat
   ```

The script will:
- Clean up old builds
- execute PyInstaller with the Windows-specific configuration
- Create the executable in `dist\AIOpsInventory\`

## 5. Run the Application

Navigate to the output folder:
`dist\AIOpsInventory\`

Double-click **AIOpsInventory.exe** to launch the application.

## Troubleshooting

- **Missing DLLs**: If you get errors about missing DLLs (like MSVCP140.dll), install the [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).
- **Icon not showing**: Ensure `resources/icon.ico` exists. If not, the build will use the default icon.
- **Antivirus**: Sometimes Windows Defender may flag unsigned executables. You can add an exclusion for the `dist` folder.
