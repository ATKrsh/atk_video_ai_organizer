"""
SHA-256 file hashing utility for video identity and deduplication.
Reads files in 64KB chunks to ensure memory efficiency.
"""

import hashlib
from pathlib import Path


def compute_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute hex SHA-256 digest of a file in chunks.

    Parameters
    ----------
    file_path: Path
        Target file path.
    chunk_size: int
        Chunk size in bytes (default 64KB).

    Returns
    -------
    str
        64-character SHA-256 hex string.
    """
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
