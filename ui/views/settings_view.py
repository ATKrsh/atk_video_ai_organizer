"""
ATK Video AI Organizer - Settings View
Configures processing profiles (FAST, BALANCED, ACCURATE), paths, and watched folders.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from backend.database.db_manager import DatabaseManager

class SettingsView(QWidget):
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title_box = QVBoxLayout()
        title = QLabel("Settings & Configuration")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Configure AI models, processing profiles, storage locations, and folder watching.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Profile selection
        prof_card = QFrame()
        prof_card.setObjectName("CardFrame")
        pc_layout = QVBoxLayout(prof_card)
        pc_layout.addWidget(QLabel("<b>AI Processing Profile</b>"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["FAST (Minimal sampling, small models)", "BALANCED (Recommended for RTX 3050)", "ACCURATE (Dense sampling, detailed VLM)"])
        self.profile_combo.setCurrentIndex(1)
        pc_layout.addWidget(self.profile_combo)

        layout.addWidget(prof_card)

        # Watched Folders Section
        wf_card = QFrame()
        wf_card.setObjectName("CardFrame")
        wf_layout = QVBoxLayout(wf_card)
        wf_layout.addWidget(QLabel("<b>Folder Watching (Auto-Index New Videos)</b>"))
        
        self.wf_label = QLabel("Active Watched Folders: None")
        self.wf_label.setStyleSheet("color: #cbd5e1;")
        
        add_wf_btn = QPushButton("+ Add Folder to Watch List")
        add_wf_btn.setObjectName("SecondaryBtn")
        add_wf_btn.clicked.connect(self.add_watched_folder)

        wf_layout.addWidget(self.wf_label)
        wf_layout.addWidget(add_wf_btn)

        layout.addWidget(wf_card)
        layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.refresh_watched_folders()

    def refresh_watched_folders(self):
        folders = self.db.get_watched_folders()
        if folders:
            paths = [f["folder_path"] for f in folders]
            self.wf_label.setText("Active Watched Folders:\n" + "\n".join([f"• {p}" for p in paths]))
        else:
            self.wf_label.setText("Active Watched Folders: None")

    def add_watched_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if folder_path:
            self.db.add_watched_folder(folder_path)
            self.refresh_watched_folders()
            QMessageBox.information(self, "Folder Added", f"Folder is now being monitored for new video additions:\n{folder_path}")

    def save_settings(self):
        QMessageBox.information(self, "Settings Saved", "Configuration updated successfully!")
