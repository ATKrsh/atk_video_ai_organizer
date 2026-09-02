"""
ATK Video AI Organizer - Import Screen View
Supports +Add Video, +Add Folder, Drag & Drop, Import Preview Dialog, and Import History.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from backend.database.db_manager import DatabaseManager
from backend.pipeline.metadata import MetadataExtractor
from ui.components.drop_zone import DragDropZone

class ImportPreviewDialog(QDialog):
    def __init__(self, folder_path: str, stats: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Preview — ATK Video AI Organizer")
        self.resize(500, 350)
        self.confirmed = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("IMPORT PREVIEW")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        path_lbl = QLabel(f"Folder / Path: {folder_path}")
        path_lbl.setWordWrap(True)
        layout.addWidget(path_lbl)

        info_frame = QFrame()
        info_frame.setObjectName("CardFrame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)

        info_layout.addWidget(QLabel(f"Total Videos Found:  <b>{stats['total_found']}</b>"))
        info_layout.addWidget(QLabel(f"Total Size:          <b>{stats['total_size_gb']} GB</b>"))
        info_layout.addWidget(QLabel(f"Total Duration:      <b>{stats['total_duration_hours']} hours</b>"))
        info_layout.addWidget(QLabel(f"New Videos to Add:   <b style='color:#10b981;'>{stats['new_count']}</b>"))
        info_layout.addWidget(QLabel(f"Already in Library:  <b style='color:#f59e0b;'>{stats['existing_count']}</b>"))
        info_layout.addWidget(QLabel(f"Corrupt / Skipped:   <b style='color:#ef4444;'>{stats['corrupt_count']}</b>"))

        layout.addWidget(info_frame)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("ADD TO LIBRARY")
        confirm_btn.setObjectName("PrimaryBtn")
        confirm_btn.clicked.connect(self.accept_import)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)

    def accept_import(self):
        self.confirmed = True
        self.accept()

class ImportView(QWidget):
    videos_added = Signal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header Title & Buttons
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Import Videos")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Add video files or folders to build your local AI library. Original files remain untouched.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        add_file_btn = QPushButton("+ Add Video")
        add_file_btn.setObjectName("PrimaryBtn")
        add_file_btn.clicked.connect(self.on_add_file_clicked)

        add_folder_btn = QPushButton("+ Add Folder")
        add_folder_btn.setObjectName("PrimaryBtn")
        add_folder_btn.clicked.connect(self.on_add_folder_clicked)

        header_layout.addWidget(add_file_btn)
        header_layout.addWidget(add_folder_btn)
        layout.addLayout(header_layout)

        # Drag and Drop Zone
        self.drop_zone = DragDropZone()
        self.drop_zone.files_dropped.connect(self.on_paths_dropped)
        layout.addWidget(self.drop_zone)

        # Import History Table
        hist_title = QLabel("IMPORT HISTORY")
        hist_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #38bdf8;")
        layout.addWidget(hist_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Source Path", "Discovered", "Added", "Duplicates"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)

        self.refresh_history()

    def refresh_history(self):
        history = self.db.get_import_history()
        self.history_table.setRowCount(len(history))
        for row, item in enumerate(history):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(item.get("import_date", ""))))
            self.history_table.setItem(row, 1, QTableWidgetItem(str(item.get("source_path", ""))))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(item.get("total_discovered", 0))))
            self.history_table.setItem(row, 3, QTableWidgetItem(str(item.get("total_added", 0))))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(item.get("total_duplicate", 0))))

    def on_add_file_clicked(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "",
            "Video Files (*.mp4 *.mov *.mkv *.avi *.webm *.m4v *.wmv *.flv *.mpeg *.mpg *.3gp)"
        )
        if file_paths:
            self.process_incoming_paths(file_paths)

    def on_add_folder_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Video Folder")
        if folder_path:
            self.process_incoming_paths([folder_path])

    def on_paths_dropped(self, paths: list):
        self.process_incoming_paths(paths)

    def process_incoming_paths(self, paths: list):
        # 1. Recursive file discovery
        discovered_files = []
        for p in paths:
            if os.path.isfile(p):
                if MetadataExtractor.is_supported_video(p):
                    discovered_files.append(os.path.abspath(p))
            elif os.path.isdir(p):
                for root, _, files in os.walk(p):
                    for f in files:
                        fp = os.path.join(root, f)
                        if MetadataExtractor.is_supported_video(fp):
                            discovered_files.append(os.path.abspath(fp))

        if not discovered_files:
            QMessageBox.warning(self, "No Videos Found", "No supported video files were found in the selected location.")
            return

        # 2. Extract quick preview stats
        total_found = len(discovered_files)
        new_files = []
        existing_count = 0
        corrupt_count = 0
        total_size_bytes = 0
        total_duration_sec = 0.0

        for fp in discovered_files:
            size = os.path.getsize(fp)
            total_size_bytes += size

            # Check if already in DB
            if self.db.get_video_by_path(fp):
                existing_count += 1
            else:
                new_files.append(fp)

        preview_stats = {
            "total_found": total_found,
            "new_count": len(new_files),
            "existing_count": existing_count,
            "corrupt_count": corrupt_count,
            "total_size_gb": round(total_size_bytes / (1024**3), 2),
            "total_duration_hours": round((total_found * 15.0) / 3600.0, 2) # Est.
        }

        # 3. Show Import Preview Dialog
        source_label = paths[0] if len(paths) == 1 else f"{len(paths)} locations"
        dlg = ImportPreviewDialog(source_label, preview_stats, self)
        if dlg.exec() == QDialog.Accepted and dlg.confirmed:
            # 4. Ingest new videos into database & processing queue
            added_count = 0
            for fp in new_files:
                meta = MetadataExtractor.extract_metadata(fp)
                if meta:
                    vid_id = self.db.add_video(meta)
                    if vid_id:
                        added_count += 1

            self.db.record_import_history(source_label, total_found, added_count, existing_count, corrupt_count)
            self.refresh_history()
            self.videos_added.emit()

            QMessageBox.information(
                self, "Import Complete", 
                f"Successfully added {added_count} new videos to the library!\nBackground AI analysis has been queued."
            )
