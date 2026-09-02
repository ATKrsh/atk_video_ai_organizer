"""
ATK Video AI Organizer - Local Speech Transcription Engine
Uses faster-whisper or whisper for 100% offline audio transcription with timestamp alignment.
"""

import os
import subprocess
import shutil
from typing import List, Dict, Any
from backend.models.base_model import BaseModel
from backend.utils.logger import app_logger, error_logger

class LocalSpeechTranscriber(BaseModel):
    def __init__(self, model_name: str = "small.en", models_dir: str = "data/models", device: str = "cpu"):
        super().__init__(model_name, models_dir, device)

    def load_model(self):
        if self.is_loaded:
            return
        try:
            from faster_whisper import WhisperModel
            compute_type = "float16" if "cuda" in self.device else "int8"
            self._model = WhisperModel(self.model_name, device=self.device, compute_type=compute_type, download_root=self.models_dir)
            self.is_loaded = True
            app_logger.info(f"Loaded Speech Model ({self.model_name}) on {self.device}")
        except Exception as e:
            error_logger.error(f"Failed to load faster-whisper model: {e}")
            self.is_loaded = False

    def unload_model(self):
        if self.is_loaded:
            self._model = None
            self.is_loaded = False
            app_logger.info("Unloaded Speech Model")

    def extract_audio(self, video_path: str, wav_out_path: str) -> bool:
        """Extracts 16kHz mono WAV audio from video using ffmpeg."""
        try:
            cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le", wav_out_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return res.returncode == 0 and os.path.exists(wav_out_path) and os.path.getsize(wav_out_path) > 1000
        except Exception as e:
            error_logger.error(f"Audio extraction error for {video_path}: {e}")
            return False

    def process(self, video_path: str) -> Dict[str, Any]:
        """
        Transcribes speech in video_path.
        Returns:
          {
            "transcript_full": str,
            "language": str,
            "segments": [{"start": float, "end": float, "text": str}]
          }
        """
        wav_path = os.path.join(self.models_dir, "temp_audio.wav")
        if not self.extract_audio(video_path, wav_path):
            return {"transcript_full": "", "language": "en", "segments": []}

        if not self.is_loaded:
            self.load_model()

        if not self.is_loaded or self._model is None:
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return {"transcript_full": "", "language": "en", "segments": []}

        try:
            segments_raw, info = self._model.transcribe(wav_path, beam_size=5)
            segments = []
            full_text_parts = []
            for s in segments_raw:
                t_text = s.text.strip()
                if t_text:
                    full_text_parts.append(t_text)
                    segments.append({
                        "start": round(s.start, 2),
                        "end": round(s.end, 2),
                        "text": t_text
                    })

            if os.path.exists(wav_path):
                os.remove(wav_path)

            return {
                "transcript_full": " ".join(full_text_parts),
                "language": info.language if hasattr(info, "language") else "en",
                "segments": segments
            }
        except Exception as e:
            error_logger.error(f"Whisper transcription error: {e}")
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return {"transcript_full": "", "language": "en", "segments": []}
