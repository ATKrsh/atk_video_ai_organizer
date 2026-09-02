"""
FFprobe technical metadata extraction module using ffmpeg-python.
Extracts resolution, duration, FPS, codecs, bitrates, audio stream info.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
import ffmpeg
from logs.logger import logger


class TechnicalMetadata(BaseModel):
    duration_sec: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    container: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    raw_json: Optional[str] = None


def extract_metadata(file_path: Path) -> TechnicalMetadata:
    """Run ffprobe on target video file and parse technical metadata.

    Parameters
    ----------
    file_path: Path
        Target video file path.

    Returns
    -------
    TechnicalMetadata
        Parsed technical metadata object.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        probe_data = ffmpeg.probe(str(file_path))
    except ffmpeg.Error as e:
        logger.error(f"FFprobe error for {file_path}: {e.stderr.decode() if e.stderr else str(e)}")
        return TechnicalMetadata(raw_json=json.dumps({"error": str(e)}))

    fmt = probe_data.get("format", {})
    streams = probe_data.get("streams", [])

    meta = TechnicalMetadata()
    meta.raw_json = json.dumps(probe_data)
    meta.container = fmt.get("format_name", "").split(",")[0]
    meta.bitrate = int(fmt.get("bit_rate")) if fmt.get("bit_rate") else None
    meta.duration_sec = float(fmt.get("duration")) if fmt.get("duration") else None

    # Parse streams
    for stream in streams:
        codec_type = stream.get("codec_type")
        if codec_type == "video" and not meta.video_codec:
            meta.video_codec = stream.get("codec_name")
            meta.width = int(stream.get("width")) if stream.get("width") else None
            meta.height = int(stream.get("height")) if stream.get("height") else None

            # Calculate FPS
            r_fps = stream.get("r_frame_rate", "0/0")
            if "/" in r_fps:
                num, den = r_fps.split("/")
                if float(den) > 0:
                    meta.fps = round(float(num) / float(den), 2)

        elif codec_type == "audio" and not meta.audio_codec:
            meta.audio_codec = stream.get("codec_name")
            meta.sample_rate = int(stream.get("sample_rate")) if stream.get("sample_rate") else None
            meta.channels = int(stream.get("channels")) if stream.get("channels") else None

    logger.debug(f"Probed {file_path.name}: {meta.width}x{meta.height}, {meta.duration_sec}s, {meta.video_codec}")
    return meta
