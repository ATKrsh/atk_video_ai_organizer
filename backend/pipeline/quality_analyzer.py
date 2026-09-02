"""
ATK Video AI Organizer - Quality Analysis Engine
Calculates video quality score (0-100) based on resolution, bitrate, sharpness/blur, and FPS.
"""

import cv2
import numpy as np

class QualityAnalyzer:
    @staticmethod
    def calculate_sharpness(frame_bgr) -> float:
        """Calculates Laplacian variance as a measure of sharpness / blur."""
        try:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            return float(cv2.Laplacian(gray, cv2.CV_64F).var())
        except Exception:
            return 0.0

    @classmethod
    def evaluate_quality(cls, width: int, height: int, fps: float, bitrate: int, keyframes: list) -> dict:
        """
        Evaluates video quality and produces a score from 0 to 100.
        """
        score = 50.0 # Base score

        # 1. Resolution score (max +25 points)
        pixels = width * height
        if pixels >= 3840 * 2160: # 4K
            score += 25
        elif pixels >= 1920 * 1080: # 1080p
            score += 20
        elif pixels >= 1280 * 720: # 720p
            score += 15
        elif pixels >= 854 * 480: # 480p
            score += 10

        # 2. Bitrate score (max +15 points)
        if bitrate > 10_000_000: # 10 Mbps+
            score += 15
        elif bitrate > 4_000_000: # 4 Mbps+
            score += 10
        elif bitrate > 1_500_000: # 1.5 Mbps+
            score += 5

        # 3. FPS score (max +10 points)
        if fps >= 50:
            score += 10
        elif fps >= 24:
            score += 7
        elif fps >= 15:
            score += 3

        # 4. Sharpness score (max +10 points)
        sharpness_list = []
        for sample in keyframes[:5]:
            if "frame_bgr" in sample:
                sharpness_list.append(cls.calculate_sharpness(sample["frame_bgr"]))

        avg_sharpness = float(np.mean(sharpness_list)) if sharpness_list else 0.0
        if avg_sharpness > 300:
            score += 10
        elif avg_sharpness > 100:
            score += 7
        elif avg_sharpness > 30:
            score += 4

        final_score = int(min(100, max(0, score)))

        notes = []
        if pixels >= 1920 * 1080:
            notes.append("High Resolution")
        if avg_sharpness > 150:
            notes.append("Sharp Focus")
        if bitrate > 3_000_000:
            notes.append("High Bitrate")

        return {
            "quality_score": final_score,
            "sharpness": round(avg_sharpness, 1),
            "quality_notes": ", ".join(notes) if notes else "Standard Quality"
        }
