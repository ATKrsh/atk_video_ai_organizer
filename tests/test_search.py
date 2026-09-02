"""
ATK Video AI Organizer - Automated Unit Tests for Hybrid Natural Language Search
"""

import os
import unittest
from backend.database.db_manager import DatabaseManager
from backend.models.embedding_model import LocalEmbeddingGenerator
from backend.search.vector_store import LocalVectorStore
from backend.search.hybrid_search import HybridSearchEngine

class TestHybridSearch(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.abspath("data/test_search_unit.db")
        self.db = DatabaseManager(self.db_path)
        self.emb = LocalEmbeddingGenerator()
        self.vstore = LocalVectorStore(self.db)
        self.engine = HybridSearchEngine(self.db, self.emb, self.vstore)

    def tearDown(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_query_parsing(self):
        parsed = self.engine.parse_natural_query("find videos from 2024 containing motorcycles at night")
        self.assertEqual(parsed["filters"].get("year"), "2024")
        self.assertEqual(parsed["filters"].get("environment"), "night")

    def test_hybrid_search_results(self):
        v1 = {
            "original_path": "D:\\Videos\\dog.mp4",
            "filename": "dog.mp4",
            "file_size": 1000,
            "category": "Animals"
        }
        vid1 = self.db.add_video(v1)
        self.db.update_video_analysis(vid1, "A cute dog running in a park.", "Animals", ["dog", "park"], 85, "High Quality")

        results = self.engine.search("dog running")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], vid1)
        self.assertIn("dog", results[0]["match_reasons"][0].lower())

if __name__ == "__main__":
    unittest.main()
