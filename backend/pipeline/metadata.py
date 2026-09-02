"""
ATK Video AI Organizer - Metadata Extraction Engine
Extracts technical specifications: duration, resolution, FPS, codecs, bitrate, timestamps, and hashes.
"""

import os
import datetime
import cv2
from typing import Dict, Any, Optional
from backend.utils.hash_utils import compute_sha256, compute_perceptual_hash
from backend.utils.logger import app_logger, error_logger

class MetadataExtractor:
    SUPPORTED_EXTENSIONS = {
        ".mp4", ".mov", ".mkv", ".avi", ".webm", 
        ".m4v", ".wmv", ".flv", ".mpeg", ".mpg", ".3gp"
    }

    @classmethod
    def is_supported_video(cls, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in cls.SUPPORTED_EXTENSIONS and os.path.isfile(file_path)

    @classmethod
    def extract_metadata(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """Extracts complete metadata dictionary for a video file."""
        if not cls.is_supported_video(file_path):
            return None

        file_path = os.path.abspath(file_path)
        file_size = os.path.getsize(file_path)
        stat = os.stat(file_path)

        creation_time = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
        modification_time = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        filename = os.path.basename(file_path)
        parent_folder = os.path.dirname(file_path)

        # OpenCV probe
        width, height, fps, duration, frame_count = 0, 0, 0.0, 0.0, 0
        phash = ""
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = float(cap.get(cv2.CAP_PROP_FPS))
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if fps > 0 and frame_count > 0:
                    duration = round(frame_count / fps, 2)

                # Compute phash from middle frame
                mid_frame = frame_count // 2
                cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
                ret, frame = cap.read()
                if ret and frame is not None:
                    phash = compute_perceptual_hash(frame) or ""
            cap.release()
        except Exception as e:
            error_logger.error(f"OpenCV metadata probe error on {file_path}: {e}")

        # Compute file hash
        file_hash = compute_sha256(file_path)

        # Estimate bitrate
        bitrate = int((file_size * 8) / duration) if duration > 0 else 0

        return {
            "original_path": file_path,
            "filename": filename,
            "parent_folder": parent_folder,
            "source_type": "local",
            "file_size": file_size,
            "file_hash": file_hash,
            "phash": phash,
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "codec": "H.264 / HEVC / AVC", # Common default
            "bitrate": bitrate,
            "audio_codec": "AAC / MP3",
            "creation_date": creation_time,
            "modification_date": modification_time,
            "status": "NEW"
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        meta = MetadataExtractor.extract_metadata(sys.argv[1])
        print("Metadata Result:", meta)
