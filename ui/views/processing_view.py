"""
ATK Video AI Organizer - Processing Queue View
Displays active background AI analysis progress, job queue, VRAM usage, and pause/resume controls.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from backend.database.db_manager import DatabaseManager
from backend.pipeline.processor import PipelineProcessor

class ProcessingView(QWidget):
    def __init__(self, db_manager: DatabaseManager, processor: PipelineProcessor, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.processor = processor
        self.init_ui()

        # Connect progress updates
        if self.processor:
            self.processor.progress_callback = self.on_processor_progress

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header Title & Controls
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("AI Processing Queue")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Background local video analysis queue (YOLO + Whisper + VLM + Embeddings).")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        self.pause_btn = QPushButton("⏸ Pause Queue")
        self.pause_btn.setObjectName("SecondaryBtn")
        self.pause_btn.clicked.connect(self.toggle_pause)

        self.resume_btn = QPushButton("▶ Resume Queue")
        self.resume_btn.setObjectName("PrimaryBtn")
        self.resume_btn.clicked.connect(self.toggle_resume)
        self.resume_btn.hide()

        header.addWidget(self.pause_btn)
        header.addWidget(self.resume_btn)
        layout.addLayout(header)

        # Active Job Card
        active_card = QFrame()
        active_card.setObjectName("CardFrame")
        ac_layout = QVBoxLayout(active_card)
        ac_layout.setContentsMargins(20, 20, 20, 20)

        self.curr_vid_lbl = QLabel("Current Video: <b>None in queue</b>")
        self.curr_vid_lbl.setStyleSheet("font-size: 14px;")

        self.curr_stage_lbl = QLabel("Current Stage: Idle")
        self.curr_stage_lbl.setStyleSheet("color: #38bdf8; font-weight: bold;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        ac_layout.addWidget(self.curr_vid_lbl)
        ac_layout.addWidget(self.curr_stage_lbl)
        ac_layout.addWidget(self.progress_bar)

        layout.addWidget(active_card)

        # Job Queue Table
        q_title = QLabel("QUEUE STATUS HISTORY")
        q_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #38bdf8;")
        layout.addWidget(q_title)

        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(4)
        self.queue_table.setHorizontalHeaderLabels(["Video Filename", "Stage", "Progress", "Status"])
        self.queue_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.queue_table)

        self.refresh_queue_table()

    def toggle_pause(self):
        if self.processor:
            self.processor.pause()
            self.pause_btn.hide()
            self.resume_btn.show()

    def toggle_resume(self):
        if self.processor:
            self.processor.resume()
            self.resume_btn.hide()
            self.pause_btn.show()

    def on_processor_progress(self, info: dict):
        self.curr_vid_lbl.setText(f"Current Video: <b>{info.get('filename')}</b>")
        self.curr_stage_lbl.setText(f"Stage: <b>{info.get('stage')}</b> (GPU VRAM: {info.get('gpu_vram')})")
        self.progress_bar.setValue(info.get("progress_pct", 0))
        self.refresh_queue_table()

    def refresh_queue_table(self):
        conn = self.db.get_connection()
        rows = conn.execute("""
            SELECT j.*, v.filename 
            FROM analysis_jobs j 
            JOIN videos v ON j.video_id = v.id 
            ORDER BY j.id DESC LIMIT 30;
        """).fetchall()

        self.queue_table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.queue_table.setItem(row, 0, QTableWidgetItem(str(r["filename"])))
            self.queue_table.setItem(row, 1, QTableWidgetItem(str(r["current_stage"])))
            self.queue_table.setItem(row, 2, QTableWidgetItem(f"{r['progress_pct']}%"))
            self.queue_table.setItem(row, 3, QTableWidgetItem(str(r["status"])))
