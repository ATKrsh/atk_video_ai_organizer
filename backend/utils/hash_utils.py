"""
ATK Video AI Organizer - Hash Utilities
Provides fast SHA-256 file hashing and video perceptual hashing.
"""

import os
import hashlib
from typing import Optional

def compute_sha256(file_path: str, chunk_size: int = 65536, max_bytes: int = 10 * 1024 * 1024) -> str:
    """
    Computes a fast SHA-256 hash of the file.
    For large files, reads head, middle, and tail chunks to achieve maximum speed.
    """
    if not os.path.exists(file_path):
        return ""
    
    file_size = os.path.getsize(file_path)
    hasher = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            if file_size <= max_bytes:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            else:
                # Head 3MB
                hasher.update(f.read(3 * 1024 * 1024))
                # Middle 3MB
                f.seek(file_size // 2)
                hasher.update(f.read(3 * 1024 * 1024))
                # Tail 3MB
                f.seek(max(0, file_size - 3 * 1024 * 1024))
                hasher.update(f.read(3 * 1024 * 1024))
                # Include file size in hash
                hasher.update(str(file_size).encode("utf-8"))

        return hasher.hexdigest()
    except Exception as e:
        print(f"SHA256 error on {file_path}: {e}")
        return ""

def compute_perceptual_hash(frame_bgr) -> Optional[str]:
    """Computes a perceptual hash (dhash) from a video frame."""
    try:
        import imagehash
        from PIL import Image
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        return str(imagehash.dhash(pil_img))
    except Exception:
        return None
