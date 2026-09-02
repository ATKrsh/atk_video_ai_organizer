@echo off
TITLE ATK Video AI Organizer — Executable Builder
COLOR 0A
cd /d "%~dp0"

echo =======================================================================
echo          BUILDING ATK_VIDEO_AI_ORGANIZER_V1.EXE STANDALONE BUILD
echo =======================================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

pip install pyinstaller

echo [INFO] Compiling ATK_Video_AI_Organizer_v1.exe...
pyinstaller --noconfirm --onefile --windowed --name "ATK_Video_AI_Organizer_v1" --add-data "config.json;." --add-data "ui/styles;ui/styles" app.py

echo.
if exist "dist\ATK_Video_AI_Organizer_v1.exe" (
    echo =======================================================================
    echo SUCCESS! Standalone executable compiled to:
    echo dist\ATK_Video_AI_Organizer_v1.exe
    echo =======================================================================
) else (
    echo [ERROR] Compilation failed.
)
pause
