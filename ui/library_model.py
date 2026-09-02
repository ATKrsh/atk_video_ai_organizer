"""
Qt model exposing video records for a QTableView.
"""
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Any
from database.database import SessionLocal
from database.schema import Video, VideoFile

class LibraryModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._load_data()

    def _load_data(self):
        session = SessionLocal()
        try:
            results = (
                session.query(Video, VideoFile)
                .join(VideoFile, Video.file_id == VideoFile.id)
                .all()
            )
            self._rows = [
                {
                    "path": vf.path,
                    "size": vf.size,
                    "sha256": vf.sha256,
                    "metadata": v.metadata,
                }
                for v, vf in results
            ]
        finally:
            session.close()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        if col == 0:
            return row["path"]
        if col == 1:
            return row["size"]
        if col == 2:
            return row["sha256"]
        if col == 3:
            return row["metadata"]
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ["Path", "Size (bytes)", "SHA‑256", "Metadata"][section]
        return section + 1

# Backward-compat alias
VideoLibraryModel = LibraryModel
