"""
ATK Video AI Organizer - Hardware & GPU Detector
Detects GPU, VRAM, CUDA compatibility, PyTorch CUDA status, CPU fallback, and auto-benchmarks.
"""

import sys
import subprocess
import shutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class HardwareDetector:
    def __init__(self):
        self.gpu_name = "None"
        self.total_vram_gb = 0.0
        self.free_vram_gb = 0.0
        self.cuda_available = False
        self.pytorch_cuda_available = False
        self.cpu_name = self._get_cpu_name()
        if HAS_PSUTIL:
            self.system_ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        else:
            self.system_ram_gb = 64.0 # Default fallback estimate
        self.detect_hardware()

    def _get_cpu_name(self) -> str:
        try:
            if sys.platform == "win32":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                winreg.CloseKey(key)
                return cpu_name.strip()
        except Exception:
            pass
        return "Generic CPU"

    def detect_hardware(self):
        # 1. Check NVIDIA-SMI for GPU VRAM
        if shutil.which("nvidia-smi"):
            try:
                cmd = ["nvidia-smi", "--query-gpu=gpu_name,memory.total,memory.free", "--format=csv,noheader,nounits"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    parts = [p.strip() for p in result.stdout.strip().split(",")]
                    if len(parts) >= 3:
                        self.gpu_name = parts[0]
                        self.total_vram_gb = round(float(parts[1]) / 1024.0, 2)
                        self.free_vram_gb = round(float(parts[2]) / 1024.0, 2)
                        self.cuda_available = True
            except Exception as e:
                print(f"[HardwareDetector] nvidia-smi query error: {e}")

        # 2. Check PyTorch CUDA if PyTorch is installed
        try:
            import torch
            self.pytorch_cuda_available = torch.cuda.is_available()
            if self.pytorch_cuda_available:
                self.gpu_name = torch.cuda.get_device_name(0)
                mem = torch.cuda.get_device_properties(0).total_memory
                self.total_vram_gb = round(mem / (1024**3), 2)
                self.cuda_available = True
        except ImportError:
            self.pytorch_cuda_available = False

    def get_summary(self) -> dict:
        mode = "GPU (CUDA Accelerated)" if (self.cuda_available or self.pytorch_cuda_available) else "CPU (Fallback Mode)"
        selected_vlm = "Florence-2-base (Optimized for RTX 3050)" if self.free_vram_gb >= 4.0 else "MobileVLM / Fast Tagging"
        return {
            "gpu": self.gpu_name if self.gpu_name != "None" else "No NVIDIA GPU Detected",
            "vram_total": f"{self.total_vram_gb} GB",
            "vram_free": f"{self.free_vram_gb} GB",
            "cuda": "Available" if self.cuda_available else "Not Detected",
            "pytorch_cuda": "Enabled" if self.pytorch_cuda_available else "PyTorch CUDA package needed",
            "cpu": self.cpu_name,
            "ram": f"{self.system_ram_gb} GB",
            "selected_models": f"YOLOv8s + Whisper-small + {selected_vlm} + CLIP",
            "processing_mode": mode
        }

    def print_startup_banner(self):
        summary = self.get_summary()
        print("=" * 65)
        print("   ATK VIDEO AI ORGANIZER — HARDWARE DIAGNOSTICS")
        print("=" * 65)
        print(f"  CPU            : {summary['cpu']}")
        print(f"  System RAM     : {summary['ram']}")
        print(f"  GPU            : {summary['gpu']}")
        print(f"  VRAM           : {summary['vram_free']} free / {summary['vram_total']} total")
        print(f"  CUDA           : {summary['cuda']}")
        print(f"  PyTorch CUDA   : {summary['pytorch_cuda']}")
        print(f"  Selected Models: {summary['selected_models']}")
        print(f"  Processing Mode: {summary['processing_mode']}")
        print("=" * 65)

if __name__ == "__main__":
    detector = HardwareDetector()
    detector.print_startup_banner()
