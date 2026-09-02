"""
ATK Video AI Organizer - Intelligent Scene Detector & Smart Frame Sampler
Extracts keyframes at shot transitions and intelligent sampling intervals.
"""

import cv2
import numpy as np
from typing import List, Dict, Any

class SceneDetector:
    def __init__(self, profile: str = "BALANCED"):
        self.profile = profile
        if profile == "FAST":
            self.interval_sec = 3.0
            self.max_frames = 10
            self.diff_threshold = 30.0
        elif profile == "ACCURATE":
            self.interval_sec = 0.5
            self.max_frames = 50
            self.diff_threshold = 15.0
        else: # BALANCED
            self.interval_sec = 1.5
            self.max_frames = 20
            self.diff_threshold = 20.0

    def detect_scenes_and_sample(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Scans video, detects shot cuts, and returns list of sampled keyframes.
        Each sample dict contains:
          - frame_idx
          - timestamp_sec
          - frame_bgr
          - scene_index
          - is_scene_change (bool)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        duration_sec = total_frames / fps

        # Dynamic interval adjustment based on video length
        if duration_sec < 10:
            step_sec = 0.5
        elif duration_sec > 300:
            step_sec = 5.0
        else:
            step_sec = self.interval_sec

        step_frames = max(1, int(step_sec * fps))

        samples = []
        prev_gray = None
        scene_idx = 0

        frame_pos = 0
        while frame_pos < total_frames and len(samples) < self.max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            timestamp = frame_pos / fps
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (160, 120))

            is_change = False
            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                mean_diff = np.mean(diff)
                if mean_diff > self.diff_threshold:
                    is_change = True
                    scene_idx += 1
            prev_gray = gray

            samples.append({
                "frame_idx": frame_pos,
                "timestamp_sec": round(timestamp, 2),
                "frame_bgr": frame,
                "scene_index": scene_idx,
                "is_scene_change": is_change
            })

            frame_pos += step_frames

        cap.release()
        return samples
