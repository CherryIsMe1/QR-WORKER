@echo off
REM Runs QR-WORKER.py using the interpreter from .venv
REM If .venv doesn't exist yet, creates it and installs dependencies automatically.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo .venv not found - creating environment and installing dependencies...
    python -m venv .venv
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

".venv\Scripts\python.exe" "QR-WORKER.py"

if errorlevel 1 (
    echo.
    echo The program exited with an error. See details above.
    pause
)
