"""
Application configuration and hardware environment detector for Local AI Video Analyzer.
Detects OS, CPU, RAM, NVIDIA GPU, VRAM, CUDA, FFmpeg, and FFprobe capabilities.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from pydantic_settings import BaseSettings


class HardwareReport:
    """Detects system hardware and environment capability."""

    @staticmethod
    def detect_all() -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "cpu": platform.processor() or "Unknown CPU",
            "cpu_cores": os.cpu_count() or 1,
            "ram_gb": 0.0,
            "gpu_name": "None (CPU Fallback)",
            "vram_gb": 0.0,
            "cuda_available": False,
            "ffmpeg_available": shutil.which("ffmpeg") is not None,
            "ffprobe_available": shutil.which("ffprobe") is not None,
        }

        # RAM Detection
        try:
            import psutil
            info["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except Exception:
            pass

        # PyTorch / CUDA / GPU Detection
        try:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            if info["cuda_available"]:
                info["gpu_name"] = torch.cuda.get_device_name(0)
                info["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 1)
        except Exception:
            pass

        return info


class Settings(BaseSettings):
    """Application configuration."""

    # Base workspace directory
    base_dir: Path = Path(__file__).parent.parent.resolve()
    data_dir: Path = base_dir / "data"
    cache_dir: Path = base_dir / "cache"
    logs_dir: Path = base_dir / "logs"
    database_path: Path = data_dir / "library.db"

    # Whitelisted video extensions
    supported_extensions: List[str] = [
        ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"
    ]

    # Hardware summary
    hardware: Dict[str, Any] = HardwareReport.detect_all()

    def ensure_directories(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    class Config:
        arbitrary_types_allowed = True


settings = Settings()
settings.ensure_directories()
