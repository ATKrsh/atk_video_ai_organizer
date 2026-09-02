"""
ATK Video AI Organizer - Dashboard View
Displays high-level library statistics, hardware status, and quick action shortcuts.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from backend.database.db_manager import DatabaseManager
from backend.hardware.gpu_detector import HardwareDetector

class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, color: str = "#38bdf8", parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 32px; color: {color};")
        
        info_box = QVBoxLayout()
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #f8fafc;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")

        info_box.addWidget(val_lbl)
        info_box.addWidget(title_lbl)

        layout.addWidget(icon_lbl)
        layout.addSpacing(10)
        layout.addLayout(info_box)
        layout.addStretch()

class DashboardView(QWidget):
    navigate_to = Signal(str)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.hardware = HardwareDetector()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header Title
        title_box = QHBoxLayout()
        t_layout = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Overview of your local video AI database and GPU processing status.")
        subtitle.setStyleSheet("color: #94a3b8;")
        t_layout.addWidget(title)
        t_layout.addWidget(subtitle)
        title_box.addLayout(t_layout)
        title_box.addStretch()

        quick_import = QPushButton("📥  Import Videos")
        quick_import.setObjectName("PrimaryBtn")
        quick_import.clicked.connect(lambda: self.navigate_to.emit("import"))
        title_box.addWidget(quick_import)

        layout.addLayout(title_box)

        # Stat Cards Grid
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(15)
        layout.addLayout(self.stats_grid)

        # Hardware Info Banner
        hw_card = QFrame()
        hw_card.setObjectName("CardFrame")
        hw_layout = QVBoxLayout(hw_card)
        hw_layout.setContentsMargins(20, 15, 20, 15)

        hw_title = QLabel("💻 HARDWARE & ACCELERATION STATUS")
        hw_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #38bdf8;")
        hw_layout.addWidget(hw_title)

        summary = self.hardware.get_summary()
        self.hw_details = QLabel(
            f"GPU: <b>{summary['gpu']}</b> | VRAM Free: <b>{summary['vram_free']}</b> | "
            f"CUDA: <b>{summary['cuda']}</b> | CPU: <b>{summary['cpu']}</b> | System RAM: <b>{summary['ram']}</b>"
        )
        self.hw_details.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        hw_layout.addWidget(self.hw_details)

        layout.addWidget(hw_card)
        layout.addStretch()

        self.refresh_stats()

    def refresh_stats(self):
        stats = self.db.get_dashboard_stats()

        # Clear existing cards
        while self.stats_grid.count():
            child = self.stats_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cards_data = [
            ("Total Videos", str(stats["total_videos"]), "🎬", "#38bdf8", 0, 0),
            ("AI Indexed", str(stats["indexed_videos"]), "✅", "#10b981", 0, 1),
            ("Pending Analysis", str(stats["pending_videos"]), "⏳", "#f59e0b", 0, 2),
            ("Duplicates Found", str(stats["total_duplicates"]), "👯", "#ec4899", 1, 0),
            ("Total Duration", f"{stats['total_duration_hours']} hrs", "⏱️", "#8b5cf6", 1, 1),
            ("Total Storage", f"{stats['total_size_gb']} GB", "💾", "#06b6d4", 1, 2)
        ]

        for title, val, icon, color, r, c in cards_data:
            card = StatCard(title, val, icon, color)
            self.stats_grid.addWidget(card, r, c)
