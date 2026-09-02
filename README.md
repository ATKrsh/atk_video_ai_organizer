# ATK Video AI Organizer

**ATK Video AI Organizer** is a 100% local, privacy-preserving desktop application that analyzes, indexes, searches, categorizes, and organizes large collections of short videos using local AI models on your Windows PC.

---

## Key Features

- **100% Local & Offline**: All AI models run directly on your NVIDIA GPU / CPU. No cloud APIs, no network uploads, zero telemetry.
- **Hardware-Aware AI (RTX 3050 Optimized)**: Automatic CUDA and VRAM detection, dynamic VRAM budgeting (< 5.5 GB), batch-size adaptation, and CPU fallback.
- **First-Class Ingestion**:
  - `+ Add Video` file picker for single or multiple video files (.mp4, .mov, .mkv, .avi, .webm, .m4v, etc.)
  - `+ Add Folder` recursive scanner
  - **Drag & Drop** support for files and folders
  - Import preview modal showing total size, duration, new vs existing files, and corrupt video filtering
  - **Virtual Organization**: Original files are never copied or moved unless explicitly requested.
- **Multi-Stage AI Pipeline**:
  1. Technical Metadata Extraction & Quality Scoring (resolution, bitrate, FPS, sharpness/blur)
  2. Smart Scene Detection & Intelligent Keyframe Sampling
  3. Fast Local Object Detection (YOLOv8)
  4. OCR Text Extraction (EasyOCR / PyTesseract)
  5. Local Speech Transcription (faster-whisper with timestamps and language detection)
  6. Vision-Language Model Analysis (Florence-2 / Moondream2 natural language summaries)
  7. Vector Embeddings Generation (CLIP / MiniLM) & FAISS Vector Indexing
- **Hybrid Semantic Search**:
  - Type plain natural language queries like *"dog running outside"*, *"man riding motorcycle at night"*, *"video with Hindi speech"*
  - Hybrid scoring (Keyword match + FAISS Vector similarity + Metadata filtering)
  - **Explainable Match Reasons** showing why each video matched your search query.
- **Duplicate & Quality Management**:
  - Exact duplicates (SHA-256 hash)
  - Near duplicates (Perceptual hash re-encoding/resize detection)
  - Semantic duplicates (vector similarity)
  - Automatic *"Keep Recommended"* quality recommendations without destructive deletion.
- **Interruptible & Resumable Queue**: Background job processing queue with Pause, Resume, and restart persistence.
- **CLI Commands**: Full command-line support (`python app.py scan`, `analyze`, `search`, `duplicates`, `export`).

---

## Technology Stack

- **Desktop UI**: PySide6 (Qt 6 for Python) with modern dark QSS theme & Qt QMediaPlayer
- **Database**: SQLite with WAL mode & FAISS vector index
- **AI Core**: PyTorch, CUDA, YOLOv8 (`ultralytics`), faster-whisper, EasyOCR, Transformers (`Florence-2`), SentenceTransformers / CLIP
- **Video Engine**: OpenCV, FFmpeg / `imageio-ffmpeg`, Pillow

---

## Quick Start Guide

### 1. Installation
Double-click `install.bat` or run:
```cmd
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Running the Desktop Application
Double-click `run.bat` or run:
```cmd
python app.py
```

### 3. Using Command-Line Tools
```cmd
python app.py scan "D:\Videos"
python app.py analyze
python app.py search "man riding motorcycle"
python app.py duplicates
python app.py export --out data/export.json
```
