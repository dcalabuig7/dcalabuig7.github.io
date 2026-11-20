@echo off
REM One-time setup: installs everything and puts a "System Transcriber" shortcut on the desktop.
cd /d "%~dp0"
echo.
echo === System Transcriber setup ===
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install it from https://www.python.org/downloads/
  echo During installation, tick "Add python.exe to PATH". Then run this file again.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating a private Python environment...
  python -m venv .venv || goto :fail
)
echo Installing components (this can take a few minutes)...
".venv\Scripts\python.exe" -m pip install --upgrade pip -q
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create-shortcut.ps1" || goto :fail
echo.
echo All done! Open "System Transcriber" from your desktop.
echo The first time you transcribe, the speech model downloads (about 150 MB).
pause
exit /b 0

:fail
echo.
echo Setup failed. Scroll up to see the error.
pause
exit /b 1
