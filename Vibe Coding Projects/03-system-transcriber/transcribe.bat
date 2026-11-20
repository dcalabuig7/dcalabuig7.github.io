@echo off
REM Launcher: runs the transcriber with this folder's virtual environment.
REM Examples:
REM   transcribe live
REM   transcribe url https://www.youtube.com/watch?v=...
set "HERE=%~dp0"
if not exist "%HERE%.venv\Scripts\python.exe" (
  echo Setting up for the first time...
  python -m venv "%HERE%.venv" || exit /b 1
  "%HERE%.venv\Scripts\python.exe" -m pip install -r "%HERE%requirements.txt" || exit /b 1
)
if "%~1"=="" (
  "%HERE%.venv\Scripts\python.exe" "%HERE%transcriber.py" live
) else (
  "%HERE%.venv\Scripts\python.exe" "%HERE%transcriber.py" %*
)
