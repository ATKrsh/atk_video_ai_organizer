"""
ATK Video AI Organizer - Automated Unit Tests for Duplicate Detection
"""

import os
import unittest
from backend.database.db_manager import DatabaseManager
from backend.pipeline.duplicate_finder import DuplicateFinder

class TestDuplicateFinder(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.abspath("data/test_dup_unit.db")
        self.db = DatabaseManager(self.db_path)
        self.finder = DuplicateFinder(self.db)

    def tearDown(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_exact_duplicate_detection(self):
        v1 = {
            "original_path": "D:\\Videos\\orig.mp4",
            "filename": "orig.mp4",
            "file_size": 100000,
            "file_hash": "same_hash_12345",
            "quality_score": 90
        }
        v2 = {
            "original_path": "E:\\Backup\\copy.mp4",
            "filename": "copy.mp4",
            "file_size": 100000,
            "file_hash": "same_hash_12345",
            "quality_score": 75
        }
        self.db.add_video(v1)
        self.db.add_video(v2)

        groups = self.finder.find_all_duplicates()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["duplicate_type"], "exact")
        self.assertEqual(len(groups[0]["videos"]), 2)

if __name__ == "__main__":
    unittest.main()
