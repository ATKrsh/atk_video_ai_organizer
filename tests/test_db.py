"""
ATK Video AI Organizer - Automated Unit Tests for Database Operations
"""

import os
import unittest
from backend.database.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.abspath("data/test_db_unit.db")
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_init_db(self):
        stats = self.db.get_dashboard_stats()
        self.assertEqual(stats["total_videos"], 0)

    def test_add_video(self):
        v_data = {
            "original_path": "D:\\Videos\\test1.mp4",
            "filename": "test1.mp4",
            "parent_folder": "D:\\Videos",
            "file_size": 1024500,
            "file_hash": "abc123hash",
            "duration": 15.5,
            "width": 1920,
            "height": 1080,
            "fps": 30.0
        }
        vid_id = self.db.add_video(v_data)
        self.assertIsNotNone(vid_id)

        v_fetched = self.db.get_video_by_id(vid_id)
        self.assertEqual(v_fetched["filename"], "test1.mp4")

    def test_duplicate_path(self):
        v_data = {
            "original_path": "D:\\Videos\\dup.mp4",
            "filename": "dup.mp4",
            "file_size": 500
        }
        id1 = self.db.add_video(v_data)
        id2 = self.db.add_video(v_data)
        self.assertEqual(id1, id2)

if __name__ == "__main__":
    unittest.main()
