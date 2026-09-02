# ATK Video AI Organizer - PowerShell Installer Script
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "         ATK VIDEO AI ORGANIZER — POWERSHELL SETUP" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan

# 1. Test Python
$pythonExists = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExists) {
    Write-Host "[ERROR] Python 3.11+ is not found in PATH." -ForegroundColor Red
    Exit 1
}

# 2. Test NVIDIA GPU
$nvidiaSmiExists = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidiaSmiExists) {
    Write-Host "[OK] NVIDIA GPU detected via nvidia-smi." -ForegroundColor Green
} else {
    Write-Host "[NOTICE] NVIDIA GPU not detected. CPU fallback enabled." -ForegroundColor Yellow
}

# 3. Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating Python virtualenv..." -ForegroundColor Yellow
    python -m venv venv
}

# 4. Install dependencies
Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# 5. Make data directories
New-Item -ItemType Directory -Force -Path "data\thumbnails" | Out-Null
New-Item -ItemType Directory -Force -Path "data\models" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "=======================================================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE! Run .\run.bat or python app.py to launch." -ForegroundColor Green
Write-Host "=======================================================================" -ForegroundColor Green
