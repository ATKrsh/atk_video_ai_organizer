"""
ATK Video AI Organizer - Duplicate Management View
Displays duplicate clusters, quality comparisons, and recommendations. Never deletes automatically.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from backend.database.db_manager import DatabaseManager
from backend.pipeline.duplicate_finder import DuplicateFinder
from ui.views.library_view import VideoCard

class DuplicatesView(QWidget):
    video_selected = Signal(int)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.finder = DuplicateFinder(self.db)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header Title & Scan Button
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Duplicate Detection & Quality Comparison")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Detect exact duplicates, near duplicates (re-encoded/resized), and semantic duplicates. Originals are NEVER automatically deleted.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        scan_btn = QPushButton("🔍 Find Duplicates Now")
        scan_btn.setObjectName("PrimaryBtn")
        scan_btn.clicked.connect(self.run_duplicate_scan)
        header.addWidget(scan_btn)

        layout.addLayout(header)

        # Scroll Area for Duplicate Groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.groups_widget = QWidget()
        self.groups_layout = QVBoxLayout(self.groups_widget)
        self.groups_layout.setSpacing(20)

        scroll.setWidget(self.groups_widget)
        layout.addWidget(scroll)

        self.refresh_display()

    def run_duplicate_scan(self):
        groups = self.finder.find_all_duplicates()
        QMessageBox.information(self, "Scan Complete", f"Found {len(groups)} duplicate group(s) across your library!")
        self.refresh_display()

    def refresh_display(self):
        # Clear existing group UI
        while self.groups_layout.count():
            child = self.groups_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        conn = self.db.get_connection()
        rows = conn.execute("""
            SELECT d.group_id, d.duplicate_type, d.recommended_action, v.* 
            FROM duplicates d 
            JOIN videos v ON d.video_id = v.id 
            ORDER BY d.group_id ASC;
        """).fetchall()

        if not rows:
            no_dup = QLabel("No duplicates detected in your video collection! Click 'Find Duplicates Now' to scan.")
            no_dup.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 40px;")
            no_dup.setAlignment(Qt.AlignCenter)
            self.groups_layout.addWidget(no_dup)
            return

        # Group by group_id
        grouped = {}
        for r in rows:
            grouped.setdefault(r["group_id"], []).append(dict(r))

        for g_id, v_list in grouped.items():
            dup_type = v_list[0]["duplicate_type"].upper()
            
            group_frame = QFrame()
            group_frame.setObjectName("CardFrame")
            gf_layout = QVBoxLayout(group_frame)
            gf_layout.setContentsMargins(15, 15, 15, 15)

            g_header = QLabel(f"GROUP #{g_id} — {dup_type} DUPLICATES ({len(v_list)} files)")
            g_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #ec4899;")
            gf_layout.addWidget(g_header)

            cards_layout = QHBoxLayout()
            cards_layout.setSpacing(15)

            for item in v_list:
                item_box = QVBoxLayout()
                card = VideoCard(item)
                card.clicked.connect(lambda vid_id=item["id"]: self.video_selected.emit(vid_id))

                action_badge = QLabel(f"💡 {item['recommended_action']}")
                if "Keep" in item['recommended_action']:
                    action_badge.setStyleSheet("background-color: #065f46; color: #a7f3d0; font-weight: bold; padding: 4px; border-radius: 4px;")
                else:
                    action_badge.setStyleSheet("background-color: #7f1d1d; color: #fecaca; padding: 4px; border-radius: 4px;")

                item_box.addWidget(card)
                item_box.addWidget(action_badge)
                cards_layout.addLayout(item_box)

            cards_layout.addStretch()
            gf_layout.addLayout(cards_layout)
            self.groups_layout.addWidget(group_frame)
