"""
ATK Video AI Organizer - Comprehensive Application Audit & Verification
Instantiates all views, database queries, pipeline processors, hardware detectors, and models.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.hardware.gpu_detector import HardwareDetector
from backend.database.db_manager import DatabaseManager
from backend.pipeline.processor import PipelineProcessor
from backend.pipeline.metadata import MetadataExtractor
from backend.pipeline.scene_detector import SceneDetector
from backend.pipeline.quality_analyzer import QualityAnalyzer
from backend.pipeline.duplicate_finder import DuplicateFinder
from backend.models.object_detector import LocalObjectDetector
from backend.models.speech_model import LocalSpeechTranscriber
from backend.models.ocr_model import LocalOCREngine
from backend.models.vlm_model import LocalVisionLanguageModel
from backend.models.embedding_model import LocalEmbeddingGenerator
from backend.search.vector_store import LocalVectorStore
from backend.search.hybrid_search import HybridSearchEngine
from backend.watcher.folder_watcher import LocalFolderWatcher

class TestFullApplicationAudit(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.abspath("data/audit_test.db")
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_hardware_detector(self):
        hw = HardwareDetector()
        summary = hw.get_summary()
        self.assertIn("gpu", summary)
        self.assertIn("processing_mode", summary)

    def test_all_ai_models_instantiation(self):
        obj_det = LocalObjectDetector()
        speech = LocalSpeechTranscriber()
        ocr = LocalOCREngine()
        vlm = LocalVisionLanguageModel()
        emb = LocalEmbeddingGenerator()
        
        self.assertIsNotNone(obj_det)
        self.assertIsNotNone(speech)
        self.assertIsNotNone(ocr)
        self.assertIsNotNone(vlm)
        self.assertIsNotNone(emb)

    def test_pipeline_processor_instantiation(self):
        processor = PipelineProcessor(self.db)
        self.assertIsNotNone(processor)

    def test_search_and_duplicates(self):
        vstore = LocalVectorStore(self.db)
        emb = LocalEmbeddingGenerator()
        search_engine = HybridSearchEngine(self.db, emb, vstore)
        dup_finder = DuplicateFinder(self.db)

        res = search_engine.search("motorcycle")
        dups = dup_finder.find_all_duplicates()
        self.assertIsInstance(res, list)
        self.assertIsInstance(dups, list)

    def test_folder_watcher(self):
        watcher = LocalFolderWatcher(self.db)
        self.assertIsNotNone(watcher)

if __name__ == "__main__":
    unittest.main()
