from pathlib import Path

from media.scanner import scan_path
from logs.logger import logger

class LibraryService:
    """High‑level façade for adding video directories to the library.

    The service delegates the heavy lifting to :func:`media.scanner.scan_path` and
    returns the list of ORM ``Video`` objects that were added during the call.
    """

    def add_path(self, path: str):
        """Add a folder (or single file) to the library.

        Parameters
        ----------
        path: str
            Path to a directory (recursively scanned) or a single video file.
        """
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Path does not exist: {p}")
        logger.info(f"Scanning media path: {p}")
        added = scan_path(p)
        logger.info(f"Scanning completed – {len(added)} new videos added.")
        return added
