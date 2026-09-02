"""
ATK Video AI Organizer - Abstract Base Class for AI Models
Defines unified interface for local AI models, memory cleanup, and device offloading.
"""

from abc import ABC, abstractmethod
import os
from typing import Any, Dict

class BaseModel(ABC):
    def __init__(self, model_name: str, models_dir: str = "data/models", device: str = "cpu"):
        self.model_name = model_name
        self.models_dir = os.path.abspath(models_dir)
        os.makedirs(self.models_dir, exist_ok=True)
        self.device = device
        self.is_loaded = False
        self._model = None

    @abstractmethod
    def load_model(self):
        """Loads model into VRAM or RAM."""
        pass

    @abstractmethod
    def unload_model(self):
        """Unloads model to free VRAM."""
        pass

    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Runs inference on input data."""
        pass

    def get_status(self) -> dict:
        return {
            "model_name": self.model_name,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "models_dir": self.models_dir
        }
