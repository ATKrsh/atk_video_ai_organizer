"""
SQLAlchemy ORM models for normalized SQLite database schema.
Includes foreign keys, indexes, and full-text search schema definitions.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Index
)
from sqlalchemy.orm import relationship
from database.database import Base


class VideoFile(Base):
    __tablename__ = "video_files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False, index=True)
    filename = Column(String, nullable=False, index=True)
    sha256 = Column(String(64), unique=True, nullable=False, index=True)
    size_bytes = Column(Integer, nullable=False)
    mtime = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="file_record", uselist=False, cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False, unique=True)
    duration_sec = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    video_codec = Column(String, nullable=True)
    audio_codec = Column(String, nullable=True)
    container = Column(String, nullable=True)
    bitrate = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)
    primary_thumbnail = Column(String, nullable=True)
    analysis_status = Column(String, default="PENDING", index=True)

    # Relationships
    file_record = relationship("VideoFile", back_populates="video")
    scenes = relationship("Scene", back_populates="video", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="video", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_index = Column(Integer, nullable=False)
    start_sec = Column(Float, nullable=False, index=True)
    end_sec = Column(Float, nullable=False, index=True)
    duration_sec = Column(Float, nullable=False)
    thumbnail_path = Column(String, nullable=True)

    video = relationship("Video", back_populates="scenes")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String, nullable=False, index=True)
    progress_pct = Column(Integer, default=0)
    status = Column(String, default="QUEUED", index=True)  # QUEUED, RUNNING, PAUSED, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    video = relationship("Video", back_populates="jobs")


# Raw SQL for creating FTS5 full text search table
CREATE_FTS5_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS videos_fts USING fts5(
    filename,
    metadata_text,
    content='videos',
    content_rowid='id'
);
"""
