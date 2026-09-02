"""
ATK Video AI Organizer - Hybrid Semantic & Natural Language Search View
Provides query bar, structured filters, relevance scores, and explainable match reasons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from backend.database.db_manager import DatabaseManager
from backend.models.embedding_model import LocalEmbeddingGenerator
from backend.search.vector_store import LocalVectorStore
from backend.search.hybrid_search import HybridSearchEngine
from ui.views.library_view import VideoCard

class SearchView(QWidget):
    video_selected = Signal(int)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.embedding_gen = LocalEmbeddingGenerator()
        self.vector_store = LocalVectorStore(self.db)
        self.search_engine = HybridSearchEngine(self.db, self.embedding_gen, self.vector_store)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header Title
        title_box = QVBoxLayout()
        title = QLabel("Semantic Natural Language Search")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Search using plain natural language like 'dog running outside', 'man riding motorcycle', or 'video with Hindi speech'.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        # Search Query Bar & Filters
        search_bar = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Type any search query e.g. 'blue car at night'...")
        self.query_input.setStyleSheet("font-size: 14px; padding: 10px;")
        self.query_input.returnPressed.connect(self.run_search)

        search_btn = QPushButton("Search AI Database")
        search_btn.setObjectName("PrimaryBtn")
        search_btn.clicked.connect(self.run_search)

        search_bar.addWidget(self.query_input, stretch=4)
        search_bar.addWidget(search_btn, stretch=1)
        layout.addLayout(search_bar)

        # Results Count Header
        self.results_count_lbl = QLabel("Ready to search")
        self.results_count_lbl.setStyleSheet("font-weight: bold; color: #38bdf8;")
        layout.addWidget(self.results_count_lbl)

        # Results Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(12)

        scroll.setWidget(self.results_widget)
        layout.addWidget(scroll)

    def run_search(self):
        query = self.query_input.text().strip()
        
        # Clear results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        results = self.search_engine.search(query, top_k=30)
        self.results_count_lbl.setText(f"Found {len(results)} matching videos for '{query}'")

        if not results:
            no_res = QLabel("No matching videos found for your search query.")
            no_res.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 30px;")
            no_res.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(no_res)
            return

        for item in results:
            card_frame = QFrame()
            card_frame.setObjectName("CardFrame")
            cf_layout = QHBoxLayout(card_frame)
            cf_layout.setContentsMargins(12, 12, 12, 12)

            # Left mini video card
            mini_card = VideoCard(item)
            mini_card.clicked.connect(lambda vid_id=item["id"]: self.video_selected.emit(vid_id))

            # Right info & match reasons box
            info_box = QVBoxLayout()
            title = QLabel(f"<b>{item.get('filename')}</b>")
            title.setStyleSheet("font-size: 15px; color: #f8fafc;")
            
            score_lbl = QLabel(f"Match Score: <b style='color:#10b981;'>{item.get('match_score')}%</b>")
            
            reasons_lbl = QLabel("<b>Match Reasons:</b><br/>" + "<br/>".join([f"✓ {r}" for r in item.get("match_reasons", [])]))
            reasons_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")

            desc = QLabel(f"<i>AI Description:</i> {item.get('ai_description')}")
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #94a3b8; font-size: 12px;")

            info_box.addWidget(title)
            info_box.addWidget(score_lbl)
            info_box.addWidget(reasons_lbl)
            info_box.addWidget(desc)

            cf_layout.addWidget(mini_card)
            cf_layout.addLayout(info_box, stretch=1)

            self.results_layout.addWidget(card_frame)
