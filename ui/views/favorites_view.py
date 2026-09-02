"""
ATK Video AI Organizer - Favorites View
Displays user favorited videos and custom collections.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QScrollArea
from PySide6.QtCore import Qt, Signal
from backend.database.db_manager import DatabaseManager
from ui.views.library_view import VideoCard

class FavoritesView(QWidget):
    video_selected = Signal(int)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title_box = QVBoxLayout()
        title = QLabel("Favorites & Collections")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Quick access to your starred videos.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

        self.refresh_favorites()

    def refresh_favorites(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        conn = self.db.get_connection()
        videos = [dict(r) for r in conn.execute("SELECT * FROM videos WHERE is_favorite = 1;").fetchall()]

        if not videos:
            no_fav = QLabel("No favorite videos marked yet.")
            no_fav.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 40px;")
            no_fav.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(no_fav, 0, 0)
            return

        cols = 4
        for idx, v in enumerate(videos):
            r = idx // cols
            c = idx % cols
            card = VideoCard(v)
            card.clicked.connect(lambda vid_id=v["id"]: self.video_selected.emit(vid_id))
            self.grid_layout.addWidget(card, r, c)
