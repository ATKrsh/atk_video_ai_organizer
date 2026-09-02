"""
ATK Video AI Organizer - Video Detail View
Displays full video player, metadata, AI description, objects, speech transcript, OCR text, and actions.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QTextEdit, QScrollArea, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from backend.database.db_manager import DatabaseManager

class DetailView(QWidget):
    back_clicked = Signal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.current_video_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header with Back Button
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Library")
        back_btn.setObjectName("SecondaryBtn")
        back_btn.clicked.connect(lambda: self.back_clicked.emit())

        self.title_label = QLabel("Video Details")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        top_bar.addWidget(back_btn)
        top_bar.addSpacing(15)
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Main Split Content Area
        content_layout = QHBoxLayout()

        # Left Column: Video Player & Media Controls
        left_box = QVBoxLayout()
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(480, 270)
        self.video_widget.setStyleSheet("background-color: #000000; border-radius: 8px;")

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        controls = QHBoxLayout()
        play_btn = QPushButton("▶ Play")
        play_btn.setObjectName("SecondaryBtn")
        play_btn.clicked.connect(self.player.play)

        pause_btn = QPushButton("⏸ Pause")
        pause_btn.setObjectName("SecondaryBtn")
        pause_btn.clicked.connect(self.player.pause)

        stop_btn = QPushButton("⏹ Stop")
        stop_btn.setObjectName("SecondaryBtn")
        stop_btn.clicked.connect(self.player.stop)

        controls.addWidget(play_btn)
        controls.addWidget(pause_btn)
        controls.addWidget(stop_btn)
        controls.addStretch()

        left_box.addWidget(self.video_widget)
        left_box.addLayout(controls)

        # File Relink Warning Frame (Hidden by default)
        self.missing_frame = QFrame()
        self.missing_frame.setObjectName("CardFrame")
        self.missing_frame.setStyleSheet("border-color: #ef4444; background-color: #451a1a;")
        mf_layout = QHBoxLayout(self.missing_frame)
        self.missing_lbl = QLabel("⚠️ FILE NOT FOUND at original location!")
        self.missing_lbl.setStyleSheet("color: #fca5a5; font-weight: bold;")
        relink_btn = QPushButton("Locate File")
        relink_btn.setObjectName("PrimaryBtn")
        relink_btn.clicked.connect(self.on_locate_file_clicked)
        mf_layout.addWidget(self.missing_lbl)
        mf_layout.addStretch()
        mf_layout.addWidget(relink_btn)
        self.missing_frame.hide()

        left_box.addWidget(self.missing_frame)

        # Right Column: Metadata & AI Summaries (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)

        # AI Description Box
        desc_box = QFrame()
        desc_box.setObjectName("CardFrame")
        db_layout = QVBoxLayout(desc_box)
        db_layout.addWidget(QLabel("<b>AI Description</b>"))
        self.ai_desc_lbl = QLabel("Processing...")
        self.ai_desc_lbl.setWordWrap(True)
        self.ai_desc_lbl.setStyleSheet("color: #cbd5e1;")
        db_layout.addWidget(self.ai_desc_lbl)
        right_layout.addWidget(desc_box)

        # Technical Metadata Frame
        meta_box = QFrame()
        meta_box.setObjectName("CardFrame")
        mb_layout = QVBoxLayout(meta_box)
        mb_layout.addWidget(QLabel("<b>Technical Metadata</b>"))
        self.meta_details = QLabel()
        self.meta_details.setWordWrap(True)
        mb_layout.addWidget(self.meta_details)
        right_layout.addWidget(meta_box)

        # Detected Objects & Tags
        tag_box = QFrame()
        tag_box.setObjectName("CardFrame")
        tb_layout = QVBoxLayout(tag_box)
        tb_layout.addWidget(QLabel("<b>Category & AI Tags</b>"))
        self.tags_lbl = QLabel()
        self.tags_lbl.setWordWrap(True)
        tb_layout.addWidget(self.tags_lbl)
        right_layout.addWidget(tag_box)

        # Speech Transcript
        speech_box = QFrame()
        speech_box.setObjectName("CardFrame")
        sb_layout = QVBoxLayout(speech_box)
        sb_layout.addWidget(QLabel("<b>Speech Transcript (Whisper)</b>"))
        self.transcript_lbl = QLabel("No speech detected.")
        self.transcript_lbl.setWordWrap(True)
        sb_layout.addWidget(self.transcript_lbl)
        right_layout.addWidget(speech_box)

        scroll.setWidget(right_widget)

        content_layout.addLayout(left_box, stretch=3)
        content_layout.addWidget(scroll, stretch=4)
        layout.addLayout(content_layout)

    def load_video(self, video_id: int):
        self.current_video_id = video_id
        v = self.db.get_video_by_id(video_id)
        if not v:
            return

        self.title_label.setText(v.get("filename", "Video Details"))
        file_path = v.get("original_path", "")

        # Check if file exists on disk
        if os.path.exists(file_path):
            self.missing_frame.hide()
            self.player.setSource(QUrl.fromLocalFile(file_path))
        else:
            self.missing_frame.show()
            self.db.update_video_status(video_id, "MISSING", "File not found on disk")

        # Set Metadata Displays
        self.ai_desc_lbl.setText(v.get("ai_description") or "No description generated yet.")
        
        size_mb = round(v.get("file_size", 0) / (1024*1024), 1)
        self.meta_details.setText(
            f"Path: {v.get('original_path')}\n"
            f"Resolution: {v.get('width')}x{v.get('height')} @ {v.get('fps')} FPS\n"
            f"Duration: {v.get('duration')}s | Size: {size_mb} MB\n"
            f"Quality Score: {v.get('quality_score')}/100 ({v.get('quality_notes')})\n"
            f"Status: {v.get('status')}"
        )

        self.tags_lbl.setText(f"Category: <b>{v.get('category')}</b>\nTags: {v.get('tags_csv')}")

        # Fetch Transcript
        conn = self.db.get_connection()
        t_rows = conn.execute("SELECT timestamp_sec, text FROM transcripts WHERE video_id = ? ORDER BY timestamp_sec ASC;", (video_id,)).fetchall()
        if t_rows:
            lines = [f"[{int(r['timestamp_sec'])}s] {r['text']}" for r in t_rows]
            self.transcript_lbl.setText("\n".join(lines))
        else:
            self.transcript_lbl.setText("No speech detected.")

    def on_locate_file_clicked(self):
        new_path, _ = QFileDialog.getOpenFileName(self, "Relink Missing Video File", "", "Video Files (*.mp4 *.mov *.mkv *.avi)")
        if new_path and os.path.exists(new_path):
            conn = self.db.get_connection()
            conn.execute("UPDATE videos SET original_path = ?, status = 'ANALYZED' WHERE id = ?;", (new_path, self.current_video_id))
            conn.commit()
            QMessageBox.information(self, "File Relinked", "Video file location updated successfully!")
            self.load_video(self.current_video_id)
