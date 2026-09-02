"""
ATK Video AI Organizer - Privacy & Offline Verification Page
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class PrivacyView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel("Privacy & 100% Offline Guarantee")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("CardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("<b style='font-size:16px; color:#10b981;'>🔒 All video analysis is performed 100% locally on your computer.</b>"))
        c_layout.addWidget(QLabel("• <b>Zero Cloud Uploads:</b> No videos, frames, audio, transcripts, metadata, or embeddings are ever sent to any remote server."))
        c_layout.addWidget(QLabel("• <b>Forbidden Cloud APIs:</b> OpenAI API, Gemini API, Google Cloud AI, Claude API, Azure AI, and AWS Rekognition are completely disabled and unused."))
        c_layout.addWidget(QLabel("• <b>Offline Verification:</b> After initial setup, ATK Video AI Organizer continues to function with your Internet connection completely disabled."))
        c_layout.addWidget(QLabel("• <b>No Original File Modifications:</b> Your original video files remain untouched in their original directories."))

        layout.addWidget(card)
        layout.addStretch()
