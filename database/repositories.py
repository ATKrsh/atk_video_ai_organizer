"""
Database repository functions for CRUD operations on VideoFile, Video, and Job models.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from database.schema import VideoFile, Video, Job, Scene


def get_video_file_by_hash(session: Session, sha256: str) -> Optional[VideoFile]:
    return session.query(VideoFile).filter(VideoFile.sha256 == sha256).first()


def get_video_file_by_path(session: Session, path: str) -> Optional[VideoFile]:
    return session.query(VideoFile).filter(VideoFile.path == path).first()


def create_video_file(session: Session, path: str, filename: str, sha256: str, size_bytes: int, mtime: datetime) -> VideoFile:
    vf = VideoFile(
        path=path,
        filename=filename,
        sha256=sha256,
        size_bytes=size_bytes,
        mtime=mtime,
    )
    session.add(vf)
    session.flush()
    return vf


def create_video(session: Session, file_id: int, duration_sec: Optional[float] = None,
                 width: Optional[int] = None, height: Optional[int] = None,
                 fps: Optional[float] = None, video_codec: Optional[str] = None,
                 audio_codec: Optional[str] = None, container: Optional[str] = None,
                 bitrate: Optional[int] = None, sample_rate: Optional[int] = None,
                 channels: Optional[int] = None, metadata_json: Optional[str] = None) -> Video:
    video = Video(
        file_id=file_id,
        duration_sec=duration_sec,
        width=width,
        height=height,
        fps=fps,
        video_codec=video_codec,
        audio_codec=audio_codec,
        container=container,
        bitrate=bitrate,
        sample_rate=sample_rate,
        channels=channels,
        metadata_json=metadata_json,
        analysis_status="INDEXED",
    )
    session.add(video)
    session.flush()
    return video


def list_all_videos(session: Session) -> List[VideoFile]:
    return session.query(VideoFile).order_by(VideoFile.created_at.desc()).all()
