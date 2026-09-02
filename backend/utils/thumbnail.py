"""
ATK Video AI Organizer - Local Thumbnail Generator & Cache
Generates crisp video thumbnails and stores them locally in data/thumbnails/
"""

from typing import Optional
import os
import cv2
from PIL import Image
from backend.utils.logger import app_logger, error_logger

class ThumbnailGenerator:
    def __init__(self, cache_dir: str = "data/thumbnails"):
        self.cache_dir = os.path.abspath(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_thumbnail_path(self, video_id: int, scene_idx: int = 0) -> str:
        return os.path.join(self.cache_dir, f"vid_{video_id}_s{scene_idx}.jpeg")

    def generate_thumbnail(self, video_path: str, video_id: int, timestamp_sec: float = 1.0, width: int = 360) -> Optional[str]:
        """
        Extracts frame at timestamp_sec and saves a high quality compressed JPEG thumbnail.
        """
        out_path = self.get_thumbnail_path(video_id)
        if os.path.exists(out_path):
            return out_path

        if not os.path.exists(video_path):
            return None

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None

            # Get frame count & FPS to clamp timestamp
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1.0
            target_frame = min(int(timestamp_sec * fps), int(total_frames - 1))
            target_frame = max(0, target_frame)

            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                return None

            # Resize maintaining aspect ratio
            h, w = frame.shape[:2]
            aspect = h / float(w)
            new_w = width
            new_h = int(new_w * aspect)
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Convert to RGB & Save JPEG
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            pil_img.save(out_path, format="JPEG", quality=85)
            return out_path

        except Exception as e:
            error_logger.error(f"Thumbnail generation failed for {video_path}: {e}")
            return None
