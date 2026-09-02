"""
ATK Video AI Organizer - Local OCR Engine
Extracts text appearing in video frames (subtitles, memes, WhatsApp text, signs, watermarks).
"""

from typing import List, Dict, Any
import cv2
from backend.models.base_model import BaseModel
from backend.utils.logger import app_logger, error_logger

class LocalOCREngine(BaseModel):
    def __init__(self, model_name: str = "easyocr", models_dir: str = "data/models", device: str = "cpu"):
        super().__init__(model_name, models_dir, device)

    def load_model(self):
        if self.is_loaded:
            return
        try:
            import easyocr
            gpu_flag = "cuda" in self.device
            self._model = easyocr.Reader(['en'], gpu=gpu_flag, model_storage_directory=self.models_dir)
            self.is_loaded = True
            app_logger.info(f"Loaded EasyOCR Engine on {self.device}")
        except Exception as e:
            error_logger.error(f"Failed to load EasyOCR: {e}")
            self.is_loaded = False

    def unload_model(self):
        if self.is_loaded:
            self._model = None
            self.is_loaded = False
            app_logger.info("Unloaded OCR Engine")

    def process(self, frame_bgr) -> List[Dict[str, Any]]:
        """
        Extracts text from frame_bgr.
        Returns list of dicts: {"text": str, "confidence": float, "bbox": [...] }
        """
        if not self.is_loaded:
            self.load_model()

        if not self.is_loaded or self._model is None:
            return []

        try:
            results = self._model.readtext(frame_bgr)
            ocr_results = []
            for (bbox, text, prob) in results:
                if prob >= 0.3 and len(text.strip()) > 1:
                    ocr_results.append({
                        "text": text.strip(),
                        "confidence": round(float(prob), 2),
                        "bbox": bbox
                    })
            return ocr_results
        except Exception as e:
            error_logger.error(f"OCR inference error: {e}")
            return []
