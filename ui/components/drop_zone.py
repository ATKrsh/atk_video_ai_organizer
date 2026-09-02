"""
ATK Video AI Organizer - Drag & Drop Ingestion Zone
Accepts dropped video files and folders.
"""

import os
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt

class DragDropZone(QFrame):
    files_dropped = Signal(list) # Emits list of file/folder paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZoneArea")
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("📥")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)

        text = QLabel("Drop videos or folders here")
        text.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        text.setAlignment(Qt.AlignCenter)

        subtext = QLabel("Files (.mp4, .mov, .mkv, .avi, etc.) and Folders are recursively scanned")
        subtext.setStyleSheet("font-size: 13px; color: #94a3b8;")
        subtext.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(text)
        layout.addWidget(subtext)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #1e293b; border: 2px solid #38bdf8;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
