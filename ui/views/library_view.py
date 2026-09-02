"""
ATK Video AI Organizer - Video Library View
Grid & list view of indexed video collection with thumbnail cards, category badges, and filters.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QComboBox, QScrollArea, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from backend.database.db_manager import DatabaseManager
from backend.utils.thumbnail import ThumbnailGenerator

class VideoCard(QFrame):
    clicked = Signal(int) # Emits video_id

    def __init__(self, video_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.video_id = video_data["id"]
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(220, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Thumbnail Image Label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(204, 120)
        self.thumb_label.setStyleSheet("background-color: #0f172a; border-radius: 4px;")
        self.thumb_label.setAlignment(Qt.AlignCenter)

        # Load thumbnail image
        thumb_gen = ThumbnailGenerator()
        thumb_path = thumb_gen.get_thumbnail_path(self.video_id)
        if os.path.exists(thumb_path):
            pixmap = QPixmap(thumb_path)
            self.thumb_label.setPixmap(pixmap.scaled(204, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.thumb_label.setText("🎬")

        # Filename
        filename = QLabel(video_data.get("filename", "Untitled"))
        filename.setStyleSheet("font-weight: bold; font-size: 12px; color: #f8fafc;")
        filename.setWordWrap(True)

        # Category Badge & Duration
        meta_row = QHBoxLayout()
        cat_badge = QLabel(video_data.get("category", "Uncategorized"))
        cat_badge.setStyleSheet("background-color: #334155; color: #38bdf8; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
        
        dur_sec = video_data.get("duration", 0.0)
        dur_badge = QLabel(f"{int(dur_sec)}s")
        dur_badge.setStyleSheet("color: #94a3b8; font-size: 11px;")

        meta_row.addWidget(cat_badge)
        meta_row.addStretch()
        meta_row.addWidget(dur_badge)

        # Status badge
        status = video_data.get("status", "NEW")
        status_lbl = QLabel(f"Status: {status}")
        status_lbl.setStyleSheet("font-size: 10px; color: #64748b;")

        layout.addWidget(self.thumb_label)
        layout.addWidget(filename)
        layout.addLayout(meta_row)
        layout.addWidget(status_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.video_id)

class LibraryView(QWidget):
    video_selected = Signal(int)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header Controls
        header = QHBoxLayout()
        title = QLabel("Video Library")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter videos by name, tag, description...")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self.refresh_library)
        header.addWidget(self.search_input)

        self.cat_filter = QComboBox()
        self.cat_filter.addItem("All Categories")
        for cat in [
            "People", "Animals", "Vehicles", "Technology", "Nature", "Food", 
            "Travel", "Sports", "Gaming", "Memes", "Funny", "Music", "Dance", 
            "Tutorials", "News", "Family", "Work", "Screenshots", "Miscellaneous"
        ]:
            self.cat_filter.addItem(cat)
        self.cat_filter.currentTextChanged.connect(self.refresh_library)
        header.addWidget(self.cat_filter)

        layout.addLayout(header)

        # Scroll Area for Video Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        self.refresh_library()

    def refresh_library(self):
        # Clear grid
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        search = self.search_input.text().strip() or None
        cat = self.cat_filter.currentText()
        if cat == "All Categories":
            cat = None

        videos = self.db.get_all_videos(limit=100, category=cat, search=search)

        if not videos:
            no_vid = QLabel("No videos found in library. Click '+ Add Video' or '+ Add Folder' to import.")
            no_vid.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 40px;")
            no_vid.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(no_vid, 0, 0)
            return

        cols = 4
        for idx, v in enumerate(videos):
            r = idx // cols
            c = idx % cols
            card = VideoCard(v)
            card.clicked.connect(lambda vid_id: self.video_selected.emit(vid_id))
            self.grid_layout.addWidget(card, r, c)
