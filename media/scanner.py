"""
Recursive video scanner and file importer.
Stores original filesystem paths, SHA-256 hashes, and technical metadata in SQLite DB.
Never copies, moves, or alters source videos.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional

from config.settings import settings
from database.database import SessionLocal
from database.schema import VideoFile, Video
from database.repositories import (
    get_video_file_by_hash, get_video_file_by_path,
    create_video_file, create_video
)
from media.hashing import compute_sha256
from media.probe import extract_metadata
from logs.logger import logger


def is_supported_video(path: Path) -> bool:
    """Check if file extension is in supported whitelist."""
    return path.is_file() and path.suffix.lower() in settings.supported_extensions


def discover_video_files(root: Path) -> List[Path]:
    """Recursively discover supported video files under target path."""
    found: List[Path] = []
    if root.is_file():
        if is_supported_video(root):
            found.append(root)
    elif root.is_dir():
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                fp = Path(dirpath) / f
                if is_supported_video(fp):
                    found.append(fp)
    return found


def add_video_file_to_db(session, file_path: Path) -> Optional[VideoFile]:
    """Compute SHA-256, probe metadata, and save VideoFile & Video to DB if not present."""
    path_str = str(file_path.resolve())

    # Check by path
    existing_by_path = get_video_file_by_path(session, path_str)
    if existing_by_path:
        logger.debug(f"Already indexed by path: {path_str}")
        return existing_by_path

    # Compute SHA-256
    sha256 = compute_sha256(file_path)

    # Check by hash (detect duplicate files in different locations)
    existing_by_hash = get_video_file_by_hash(session, sha256)
    if existing_by_hash:
        logger.info(f"Duplicate file hash detected: {path_str} matches existing ID {existing_by_hash.id}")
        return existing_by_hash

    # Get file stat
    stat = file_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)

    # Extract technical metadata
    meta = extract_metadata(file_path)

    # Insert DB records
    vf = create_video_file(
        session=session,
        path=path_str,
        filename=file_path.name,
        sha256=sha256,
        size_bytes=stat.st_size,
        mtime=mtime,
    )

    create_video(
        session=session,
        file_id=vf.id,
        duration_sec=meta.duration_sec,
        width=meta.width,
        height=meta.height,
        fps=meta.fps,
        video_codec=meta.video_codec,
        audio_codec=meta.audio_codec,
        container=meta.container,
        bitrate=meta.bitrate,
        sample_rate=meta.sample_rate,
        channels=meta.channels,
        metadata_json=meta.raw_json,
    )

    session.commit()
    logger.info(f"Successfully indexed video: {file_path.name} ({sha256[:8]}...)")
    return vf


def scan_and_store(root_path: Path) -> List[VideoFile]:
    """High-level entry point: scan root_path and store all new videos in DB."""
    session = SessionLocal()
    added: List[VideoFile] = []
    try:
        discovered = discover_video_files(root_path)
        logger.info(f"Discovered {len(discovered)} video files under {root_path}")
        for fp in discovered:
            try:
                vf = add_video_file_to_db(session, fp)
                if vf:
                    added.append(vf)
            except Exception as e:
                logger.error(f"Failed indexing file {fp}: {e}")
                session.rollback()
    finally:
        session.close()
    return added


def scan_path(target_path: Path) -> List[VideoFile]:
    """Alias for scan_and_store."""
    return scan_and_store(target_path)
