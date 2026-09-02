@echo off
TITLE ATK Video AI Organizer — Windows Installation
COLOR 0A
echo =======================================================================
echo           ATK VIDEO AI ORGANIZER — 100%% LOCAL WINDOWS INSTALLER
echo =======================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11 or 3.12 and check 'Add Python to PATH'.
    pause
    exit /b 1
)
echo [OK] Python detected.

:: 2. Check NVIDIA GPU / CUDA
nvidia-smi >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] NVIDIA GPU & CUDA driver detected.
) else (
    echo [WARNING] NVIDIA GPU / CUDA driver not found. Application will run in CPU fallback mode.
)

:: 3. Create virtual environment if missing
if not exist "venv" (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
)

:: 4. Activate venv & Install dependencies
echo [INFO] Installing required Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 5. Initialize directories & Database
if not exist "data\thumbnails" mkdir data\thumbnails
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs

echo [INFO] Initializing SQLite database...
python -c "from backend.database.db_manager import DatabaseManager; db = DatabaseManager(); print('[OK] Database initialized at data/atk_video_organizer.db')"

echo.
echo =======================================================================
echo           INSTALLATION COMPLETE! YOU CAN NOW LAUNCH THE APP.
echo           To run the application, double click 'run.bat'
echo =======================================================================
pause
