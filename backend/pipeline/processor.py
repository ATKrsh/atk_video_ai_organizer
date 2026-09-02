"""
ATK Video AI Organizer - Interruptible AI Pipeline Processor & Job Queue Manager
Orchestrates multi-stage processing with pause/resume, VRAM offloading, and corrupt video tolerance.
"""

import threading
import time
from typing import Optional, Callable
from backend.database.db_manager import DatabaseManager
from backend.hardware.gpu_detector import HardwareDetector
from backend.utils.thumbnail import ThumbnailGenerator
from backend.pipeline.metadata import MetadataExtractor
from backend.pipeline.scene_detector import SceneDetector
from backend.pipeline.quality_analyzer import QualityAnalyzer
from backend.models.object_detector import LocalObjectDetector
from backend.models.speech_model import LocalSpeechTranscriber
from backend.models.ocr_model import LocalOCREngine
from backend.models.vlm_model import LocalVisionLanguageModel
from backend.models.embedding_model import LocalEmbeddingGenerator
from backend.search.vector_store import LocalVectorStore
from backend.utils.logger import app_logger, error_logger

class PipelineProcessor:
    def __init__(self, db_manager: DatabaseManager, profile: str = "BALANCED"):
        self.db = db_manager
        self.profile = profile
        self.hardware = HardwareDetector()
        self.device = "cuda" if self.hardware.cuda_available else "cpu"
        
        self.thumbnail_gen = ThumbnailGenerator()
        self.scene_detector = SceneDetector(profile=profile)
        self.object_detector = LocalObjectDetector(device=self.device)
        self.speech_transcriber = LocalSpeechTranscriber(device=self.device)
        self.ocr_engine = LocalOCREngine(device=self.device)
        self.vlm_model = LocalVisionLanguageModel(device=self.device)
        self.embedding_gen = LocalEmbeddingGenerator(device=self.device)
        self.vector_store = LocalVectorStore(self.db)

        self.is_running = False
        self.is_paused = False
        self._thread = None
        self.current_video_path = ""
        self.progress_callback: Optional[Callable[[dict], None]] = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._thread = threading.Thread(target=self._process_queue_loop, daemon=True)
        self._thread.start()
        app_logger.info("Pipeline Processor thread started")

    def pause(self):
        self.is_paused = True
        app_logger.info("Pipeline Processor paused")

    def resume(self):
        self.is_paused = False
        app_logger.info("Pipeline Processor resumed")

    def stop(self):
        self.is_running = False
        self.is_paused = False
        app_logger.info("Pipeline Processor stopped")

    def _notify_progress(self, video_id: int, stage: str, progress_pct: int, filename: str):
        if self.progress_callback:
            self.progress_callback({
                "video_id": video_id,
                "stage": stage,
                "progress_pct": progress_pct,
                "filename": filename,
                "gpu_vram": f"{self.hardware.free_vram_gb} GB"
            })

    def _process_queue_loop(self):
        while self.is_running:
            if self.is_paused:
                time.sleep(1.0)
                continue

            job = self.db.get_next_queued_job()
            if not job:
                time.sleep(2.0)
                continue

            video_id = job["video_id"]
            video_path = job["original_path"]
            filename = job["filename"]
            self.current_video_path = video_path

            app_logger.info(f"Starting processing for [{video_id}] {filename}")
            try:
                self.process_single_video(video_id, video_path, filename)
            except Exception as e:
                error_logger.error(f"Failed processing video {video_path}: {e}")
                self.db.update_video_status(video_id, "FAILED", str(e))
                self.db.update_job_progress(video_id, "FAILED", 0, "FAILED")

    def process_single_video(self, video_id: int, video_path: str, filename: str):
        # Stage 1: Metadata Extraction
        self._notify_progress(video_id, "Extracting Metadata", 10, filename)
        self.db.update_job_progress(video_id, "Metadata", 10)
        meta = MetadataExtractor.extract_metadata(video_path)
        if not meta:
            self.db.update_video_status(video_id, "FAILED", "Corrupt or unreadable video file")
            self.db.update_job_progress(video_id, "FAILED", 0, "FAILED")
            return

        # Stage 2: Scene Detection & Keyframe Sampling
        self._notify_progress(video_id, "Scene Detection & Keyframe Sampling", 25, filename)
        self.db.update_job_progress(video_id, "Scene Detection", 25)
        keyframes = self.scene_detector.detect_scenes_and_sample(video_path)

        # Generate primary thumbnail
        thumb_path = self.thumbnail_gen.generate_thumbnail(video_path, video_id)

        # Stage 3: Quality Scoring
        quality = QualityAnalyzer.evaluate_quality(
            meta["width"], meta["height"], meta["fps"], meta["bitrate"], keyframes
        )

        # Stage 4: Fast Object Detection
        self._notify_progress(video_id, "Object Detection (YOLO)", 45, filename)
        self.db.update_job_progress(video_id, "Object Detection", 45)
        detected_object_names = set()
        for sample in keyframes:
            if "frame_bgr" in sample:
                objs = self.object_detector.process(sample["frame_bgr"])
                for o in objs:
                    detected_object_names.add(o["object_name"])
                    # Save into database objects table
                    conn = self.db.get_connection()
                    conn.execute("""
                        INSERT INTO objects (video_id, scene_id, object_name, confidence, timestamp_sec)
                        VALUES (?, ?, ?, ?, ?);
                    """, (video_id, sample["scene_index"], o["object_name"], o["confidence"], sample["timestamp_sec"]))
                    conn.commit()

        # Stage 5: OCR Text Extraction
        self._notify_progress(video_id, "OCR Text Extraction", 60, filename)
        self.db.update_job_progress(video_id, "OCR", 60)
        ocr_text_list = []
        for sample in keyframes[::2]: # OCR every 2nd keyframe
            if "frame_bgr" in sample:
                ocr_items = self.ocr_engine.process(sample["frame_bgr"])
                for item in ocr_items:
                    ocr_text_list.append(item["text"])
                    conn = self.db.get_connection()
                    conn.execute("""
                        INSERT INTO ocr (video_id, timestamp_sec, text, confidence)
                        VALUES (?, ?, ?, ?);
                    """, (video_id, sample["timestamp_sec"], item["text"], item["confidence"]))
                    conn.commit()

        # Stage 6: Whisper Speech Transcription
        self._notify_progress(video_id, "Speech Transcription (Whisper)", 75, filename)
        self.db.update_job_progress(video_id, "Whisper Speech", 75)
        speech_res = self.speech_transcriber.process(video_path)
        transcript_text = speech_res["transcript_full"]

        if transcript_text:
            conn = self.db.get_connection()
            for seg in speech_res["segments"]:
                conn.execute("""
                    INSERT INTO transcripts (video_id, timestamp_sec, text, language)
                    VALUES (?, ?, ?, ?);
                """, (video_id, seg["start"], seg["text"], speech_res["language"]))
            conn.commit()

        # Stage 7: VLM Vision-Language Summary & Tagging
        self._notify_progress(video_id, "Vision-Language Analysis", 85, filename)
        self.db.update_job_progress(video_id, "VLM Analysis", 85)
        vlm_res = self.vlm_model.generate_video_summary(
            keyframes, list(detected_object_names), transcript_text, " ".join(ocr_text_list)
        )

        # Stage 8: Vector Embedding & FAISS Index Update
        self._notify_progress(video_id, "Generating Vector Embeddings", 95, filename)
        self.db.update_job_progress(video_id, "Embeddings", 95)
        full_text_representation = f"{filename} {vlm_res['ai_description']} {vlm_res['category']} {' '.join(vlm_res['tags'])} {transcript_text}"
        vector = self.embedding_gen.encode_text(full_text_representation)
        self.vector_store.add_embedding(video_id, vector)

        # Stage 9: Final Database Update
        self.db.update_video_analysis(
            video_id,
            vlm_res["ai_description"],
            vlm_res["category"],
            vlm_res["tags"],
            quality["quality_score"],
            quality["quality_notes"]
        )

        self.db.update_job_progress(video_id, "COMPLETED", 100, "COMPLETED")
        self._notify_progress(video_id, "Analyzed", 100, filename)
        app_logger.info(f"Successfully analyzed video [{video_id}] {filename}")
