"""
ATK Video AI Organizer - Database Schema definition for SQLite
Includes core video metadata, scenes, objects, transcripts, OCR, tags, categories, embeddings, duplicates, and job queues.
"""

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    parent_folder TEXT NOT NULL,
    source_type TEXT DEFAULT 'local',
    file_size INTEGER NOT NULL,
    file_hash TEXT,
    phash TEXT,
    duration REAL DEFAULT 0.0,
    width INTEGER DEFAULT 0,
    height INTEGER DEFAULT 0,
    fps REAL DEFAULT 0.0,
    codec TEXT DEFAULT '',
    bitrate INTEGER DEFAULT 0,
    audio_codec TEXT DEFAULT '',
    creation_date TEXT,
    modification_date TEXT,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    quality_score INTEGER DEFAULT 0,
    quality_notes TEXT DEFAULT '',
    category TEXT DEFAULT 'Uncategorized',
    tags_csv TEXT DEFAULT '',
    ai_description TEXT DEFAULT '',
    status TEXT DEFAULT 'NEW', -- NEW, QUEUED, ANALYZING, ANALYZED, FAILED, MISSING, SKIPPED
    error_message TEXT DEFAULT '',
    is_favorite INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0,
    keep_recommendation TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    scene_index INTEGER NOT NULL,
    start_sec REAL NOT NULL,
    end_sec REAL NOT NULL,
    representative_frame_path TEXT,
    description TEXT DEFAULT '',
    objects_summary TEXT DEFAULT '',
    actions_summary TEXT DEFAULT '',
    ocr_text TEXT DEFAULT '',
    transcript_segment TEXT DEFAULT '',
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    scene_id INTEGER,
    object_name TEXT NOT NULL,
    category_type TEXT DEFAULT 'general',
    confidence REAL DEFAULT 0.0,
    timestamp_sec REAL DEFAULT 0.0,
    bbox_json TEXT DEFAULT '',
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    scene_id INTEGER,
    activity_name TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    timestamp_sec REAL DEFAULT 0.0,
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    timestamp_sec REAL DEFAULT 0.0,
    text TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    confidence REAL DEFAULT 0.0,
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ocr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    timestamp_sec REAL DEFAULT 0.0,
    text TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    bbox_json TEXT DEFAULT '',
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    source TEXT DEFAULT 'ai', -- 'ai' or 'user'
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    is_custom INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER UNIQUE NOT NULL,
    vector_type TEXT DEFAULT 'clip',
    embedding_blob BLOB NOT NULL,
    dim INTEGER DEFAULT 512,
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS duplicates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    duplicate_type TEXT NOT NULL, -- 'exact', 'near', 'semantic'
    match_score REAL DEFAULT 1.0,
    recommended_action TEXT DEFAULT '',
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER UNIQUE NOT NULL,
    status TEXT DEFAULT 'QUEUED', -- QUEUED, PROCESSING, COMPLETED, FAILED, PAUSED
    current_stage TEXT DEFAULT 'INIT',
    progress_pct INTEGER DEFAULT 0,
    error_log TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(video_id) REFERENCES videos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS watched_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_path TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    auto_index INTEGER DEFAULT 1,
    last_scanned DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_path TEXT NOT NULL,
    import_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_discovered INTEGER DEFAULT 0,
    total_added INTEGER DEFAULT 0,
    total_duplicate INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Indexes for lightning fast searching
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_category ON videos(category);
CREATE INDEX IF NOT EXISTS idx_videos_path ON videos(original_path);
CREATE INDEX IF NOT EXISTS idx_videos_hash ON videos(file_hash);
CREATE INDEX IF NOT EXISTS idx_objects_name ON objects(object_name);
CREATE INDEX IF NOT EXISTS idx_transcripts_text ON transcripts(text);
CREATE INDEX IF NOT EXISTS idx_ocr_text ON ocr(text);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON analysis_jobs(status);
"""
