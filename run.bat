@echo off
TITLE ATK Video AI Organizer — Launcher
COLOR 0B
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python app.py %*
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error. Press any key to close.
    pause
)
