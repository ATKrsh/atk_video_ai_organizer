# ATK Video AI Organizer — Installation Guide

## System Prerequisites
- **Operating System**: Windows 11 (64-bit)
- **Processor**: AMD Ryzen 5 7600X / Intel Core i5 or better
- **System Memory**: 16 GB RAM minimum (64 GB recommended)
- **Graphics Card**: NVIDIA GeForce RTX 3050 (8 GB VRAM) or better with CUDA Driver 12.0+
- **Python**: Python 3.11 or 3.12 (64-bit)

---

## One-Click Installation (Windows)

1. Open the project folder `e:\workspace\atk_video_ai_organizer`.
2. Double-click **`install.bat`**.
3. The script will automatically:
   - Verify Python and NVIDIA GPU / CUDA compatibility
   - Create a virtual environment `venv`
   - Install all required Python packages (`requirements.txt`)
   - Create data directories (`data/thumbnails/`, `data/models/`, `logs/`)
   - Initialize the SQLite database `data/atk_video_organizer.db`

---

## Manual Step-by-Step Installation

If you prefer to install manually using Command Prompt or PowerShell:

```cmd
:: 1. Navigate to project root
cd /d e:\workspace\atk_video_ai_organizer

:: 2. Create virtual environment
python -m venv venv

:: 3. Activate virtual environment
call venv\Scripts\activate.bat

:: 4. Upgrade pip
python -m pip install --upgrade pip

:: 5. Install PyTorch with CUDA support (Recommended for RTX 3050)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

:: 6. Install project requirements
pip install -r requirements.txt

:: 7. Initialize application
python app.py
```

---

## Model Directories & Storage

Models are downloaded and cached locally in:
```
e:\workspace\atk_video_ai_organizer\data\models\
```

After initial setup, all inference occurs 100% offline. No internet connection is required.
