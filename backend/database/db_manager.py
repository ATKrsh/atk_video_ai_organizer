"""
ATK Video AI Organizer - SQLite Database Manager
Thread-safe database operations for videos, scenes, objects, transcripts, OCR, categories, jobs, and settings.
"""

import os
import sqlite3
import threading
from typing import List, Dict, Any, Optional
from backend.database.schema import CREATE_TABLES_SQL
from backend.utils.logger import app_logger, error_logger

class DatabaseManager:
    def __init__(self, db_path: str = "data/atk_video_organizer.db"):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._local = threading.local()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path, timeout=30.0)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA foreign_keys = ON;")
            self._local.conn.execute("PRAGMA journal_mode = WAL;")
        return self._local.conn

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

    def init_db(self):
        try:
            conn = self.get_connection()
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()
            self._seed_default_categories(conn)
            app_logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            error_logger.error(f"Failed to initialize database: {e}")
            raise

    def _seed_default_categories(self, conn: sqlite3.Connection):
        default_categories = [
            "People", "Animals", "Vehicles", "Technology", "Nature", "Food", 
            "Travel", "Sports", "Gaming", "Memes", "Funny", "Music", "Dance", 
            "Tutorials", "News", "Family", "Work", "Screenshots", "Miscellaneous"
        ]
        for cat in default_categories:
            conn.execute("INSERT OR IGNORE INTO categories (name, is_custom) VALUES (?, 0);", (cat,))
        conn.commit()

    # ------------------------------------------------------------------
    # Video Ingestion & CRUD Operations
    # ------------------------------------------------------------------

    def add_video(self, video_data: Dict[str, Any]) -> Optional[int]:
        """Inserts a new video entry if not already present by path or hash."""
        conn = self.get_connection()
        try:
            # Check existing path
            existing = conn.execute("SELECT id FROM videos WHERE original_path = ?;", (video_data["original_path"],)).fetchone()
            if existing:
                return existing["id"]

            cursor = conn.execute("""
                INSERT INTO videos (
                    original_path, filename, parent_folder, source_type, file_size, 
                    file_hash, phash, duration, width, height, fps, codec, bitrate, 
                    audio_codec, creation_date, modification_date, status, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                video_data["original_path"],
                video_data["filename"],
                video_data.get("parent_folder", ""),
                video_data.get("source_type", "local"),
                video_data.get("file_size", 0),
                video_data.get("file_hash", ""),
                video_data.get("phash", ""),
                video_data.get("duration", 0.0),
                video_data.get("width", 0),
                video_data.get("height", 0),
                video_data.get("fps", 0.0),
                video_data.get("codec", ""),
                video_data.get("bitrate", 0),
                video_data.get("audio_codec", ""),
                video_data.get("creation_date", ""),
                video_data.get("modification_date", ""),
                video_data.get("status", "NEW"),
                video_data.get("category", "Uncategorized")
            ))
            conn.commit()
            video_id = cursor.lastrowid

            # Create analysis job
            conn.execute("INSERT OR IGNORE INTO analysis_jobs (video_id, status) VALUES (?, 'QUEUED');", (video_id,))
            conn.commit()
            return video_id
        except Exception as e:
            error_logger.error(f"Error adding video {video_data.get('original_path')}: {e}")
            return None

    def get_video_by_id(self, video_id: int) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM videos WHERE id = ?;", (video_id,)).fetchone()
        return dict(row) if row else None

    def get_video_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM videos WHERE original_path = ?;", (path,)).fetchone()
        return dict(row) if row else None

    def get_video_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        if not file_hash:
            return None
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM videos WHERE file_hash = ?;", (file_hash,)).fetchone()
        return dict(row) if row else None

    def get_all_videos(self, limit: int = 100, offset: int = 0, category: str = None, status: str = None, search: str = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        query = "SELECT * FROM videos WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND status = ?"
            params.append(status)

        if search:
            query += " AND (filename LIKE ? OR tags_csv LIKE ? OR ai_description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY id DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def update_video_status(self, video_id: int, status: str, error_message: str = ""):
        conn = self.get_connection()
        conn.execute("UPDATE videos SET status = ?, error_message = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?;", (status, error_message, video_id))
        conn.commit()

    def update_video_analysis(self, video_id: int, ai_description: str, category: str, tags: List[str], quality_score: int, quality_notes: str):
        conn = self.get_connection()
        tags_csv = ", ".join(tags)
        conn.execute("""
            UPDATE videos 
            SET ai_description = ?, category = ?, tags_csv = ?, quality_score = ?, quality_notes = ?, status = 'ANALYZED'
            WHERE id = ?;
        """, (ai_description, category, tags_csv, quality_score, quality_notes, video_id))
        
        # Insert tags table rows
        for t in tags:
            conn.execute("INSERT INTO tags (video_id, tag_name) VALUES (?, ?);", (video_id, t.strip().lower()))

        conn.commit()

    # ------------------------------------------------------------------
    # Job Queue Operations
    # ------------------------------------------------------------------

    def get_next_queued_job(self) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("""
            SELECT j.*, v.original_path, v.filename 
            FROM analysis_jobs j 
            JOIN videos v ON j.video_id = v.id 
            WHERE j.status = 'QUEUED' 
            ORDER BY j.id ASC LIMIT 1;
        """).fetchone()
        return dict(row) if row else None

    def update_job_progress(self, video_id: int, stage: str, progress_pct: int, status: str = "PROCESSING"):
        conn = self.get_connection()
        conn.execute("""
            UPDATE analysis_jobs 
            SET current_stage = ?, progress_pct = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE video_id = ?;
        """, (stage, progress_pct, status, video_id))
        conn.commit()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        conn = self.get_connection()
        total_videos = conn.execute("SELECT COUNT(*) FROM videos;").fetchone()[0]
        indexed_videos = conn.execute("SELECT COUNT(*) FROM videos WHERE status = 'ANALYZED';").fetchone()[0]
        pending_videos = conn.execute("SELECT COUNT(*) FROM videos WHERE status IN ('NEW', 'QUEUED', 'ANALYZING');").fetchone()[0]
        failed_videos = conn.execute("SELECT COUNT(*) FROM videos WHERE status = 'FAILED';").fetchone()[0]
        total_duration = conn.execute("SELECT SUM(duration) FROM videos;").fetchone()[0] or 0.0
        total_size = conn.execute("SELECT SUM(file_size) FROM videos;").fetchone()[0] or 0
        total_duplicates = conn.execute("SELECT COUNT(DISTINCT group_id) FROM duplicates;").fetchone()[0] or 0

        return {
            "total_videos": total_videos,
            "indexed_videos": indexed_videos,
            "pending_videos": pending_videos,
            "failed_videos": failed_videos,
            "total_duration_hours": round(total_duration / 3600.0, 2),
            "total_size_gb": round(total_size / (1024**3), 2),
            "total_duplicates": total_duplicates
        }

    # ------------------------------------------------------------------
    # Import History & Folder Watcher
    # ------------------------------------------------------------------

    def record_import_history(self, source_path: str, discovered: int, added: int, duplicate: int, failed: int):
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO import_history (source_path, total_discovered, total_added, total_duplicate, total_failed)
            VALUES (?, ?, ?, ?, ?);
        """, (source_path, discovered, added, duplicate, failed))
        conn.commit()

    def get_import_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM import_history ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def add_watched_folder(self, folder_path: str) -> bool:
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO watched_folders (folder_path, is_active) VALUES (?, 1);", (folder_path,))
            conn.commit()
            return True
        except Exception as e:
            error_logger.error(f"Error adding watched folder {folder_path}: {e}")
            return False

    def get_watched_folders(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM watched_folders WHERE is_active = 1;").fetchall()
        return [dict(r) for r in rows]

if __name__ == "__main__":
    db = DatabaseManager("data/test_db.db")
    stats = db.get_dashboard_stats()
    print("Database test stats:", stats)
