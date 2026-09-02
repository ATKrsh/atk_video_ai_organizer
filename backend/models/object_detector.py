"""
ATK Video AI Organizer - Fast Local Object Detector
Uses YOLOv8 (ultralytics) or OpenCV DNN fallback to detect objects in video frames.
"""

import os
from typing import List, Dict, Any
from backend.models.base_model import BaseModel
from backend.utils.logger import app_logger, error_logger

class LocalObjectDetector(BaseModel):
    def __init__(self, model_name: str = "yolov8s.pt", models_dir: str = "data/models", device: str = "cpu"):
        super().__init__(model_name, models_dir, device)

    def load_model(self):
        if self.is_loaded:
            return
        try:
            from ultralytics import YOLO
            model_path = f"{self.models_dir}/{self.model_name}"
            # YOLO auto downloads if not present, or uses local weights
            self._model = YOLO(model_path if self.model_name in os.listdir(self.models_dir) else self.model_name)
            self.is_loaded = True
            app_logger.info(f"Loaded Object Detector ({self.model_name}) on {self.device}")
        except Exception as e:
            error_logger.error(f"Failed to load YOLO model: {e}")
            self.is_loaded = False

    def unload_model(self):
        if self.is_loaded:
            self._model = None
            self.is_loaded = False
            app_logger.info("Unloaded Object Detector")

    def process(self, frame_bgr) -> List[Dict[str, Any]]:
        """
        Detects objects in a single BGR frame.
        Returns list of dicts: {"object_name": str, "confidence": float, "bbox": [x1, y1, x2, y2]}
        """
        if not self.is_loaded:
            self.load_model()

        if not self.is_loaded or self._model is None:
            # Fallback heuristic detector when YOLO weights not present
            return self._heuristic_fallback(frame_bgr)

        try:
            results = self._model(frame_bgr, verbose=False, device=0 if "cuda" in self.device else "cpu")
            detections = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    name = r.names[cls_id]
                    conf = float(box.conf[0])
                    coords = [float(x) for x in box.xyxy[0]]
                    if conf >= 0.25:
                        detections.append({
                            "object_name": name,
                            "confidence": round(conf, 2),
                            "bbox": [round(c, 1) for c in coords]
                        })
            return detections
        except Exception as e:
            error_logger.error(f"Object detection inference error: {e}")
            return self._heuristic_fallback(frame_bgr)

    def _heuristic_fallback(self, frame_bgr) -> List[Dict[str, Any]]:
        """Simple OpenCV background/contour heuristic fallback."""
        import cv2
        import numpy as np
        detections = []
        try:
            h, w = frame_bgr.shape[:2]
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            # Basic face/person heuristic via Haar cascade if available
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, fw, fh) in faces:
                detections.append({
                    "object_name": "person",
                    "confidence": 0.85,
                    "bbox": [float(x), float(y), float(x+fw), float(y+fh)]
                })
        except Exception:
            pass
        return detections
