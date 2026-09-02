"""
ATK Video AI Organizer - Categories & Collections View
Virtual category manager and optional File Organization preview tool.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox, QDialog
)
from PySide6.QtCore import Qt
from backend.database.db_manager import DatabaseManager

class OrganizationPreviewDialog(QDialog):
    def __init__(self, category_name: str, move_count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Organize Files Preview — ATK Video AI Organizer")
        self.resize(450, 280)
        self.confirmed = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("OPTIONAL FILE ORGANIZATION PREVIEW")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f59e0b;")
        layout.addWidget(title)

        warn_box = QFrame()
        warn_box.setObjectName("CardFrame")
        wb_layout = QVBoxLayout(warn_box)
        wb_layout.addWidget(QLabel("<b>IMPORTANT SAFETY RULE:</b>"))
        wb_layout.addWidget(QLabel("Original video files are indexed virtually. Moving or copying files on disk is completely optional."))
        wb_layout.addWidget(QLabel(f"Target Category: <b>{category_name}</b>"))
        wb_layout.addWidget(QLabel(f"Files Affected: <b>{move_count} files</b>"))
        layout.addWidget(warn_box)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        copy_btn = QPushButton("COPY Files")
        copy_btn.setObjectName("PrimaryBtn")
        copy_btn.clicked.connect(lambda: self.set_action("COPY"))

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(copy_btn)
        layout.addLayout(btn_box)

    def set_action(self, act: str):
        self.confirmed = True
        self.action = act
        self.accept()

class CategoriesView(QWidget):
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title_box = QVBoxLayout()
        title = QLabel("Categories & Virtual Organization")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Organize videos into virtual categories without moving your actual files.")
        subtitle.setStyleSheet("color: #94a3b8;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        content = QHBoxLayout()
        
        # Category list
        self.cat_list = QListWidget()
        self.cat_list.setStyleSheet("font-size: 14px;")
        self.cat_list.currentTextChanged.connect(self.on_category_selected)
        content.addWidget(self.cat_list, stretch=1)

        # Right Category Action Box
        action_box = QFrame()
        action_box.setObjectName("CardFrame")
        ab_layout = QVBoxLayout(action_box)
        ab_layout.setSpacing(15)

        self.cat_header = QLabel("Select a Category")
        self.cat_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        self.cat_count_lbl = QLabel("Videos in category: 0")

        org_btn = QPushButton("📁 Optional: Organize Files On Disk...")
        org_btn.setObjectName("PrimaryBtn")
        org_btn.clicked.connect(self.on_organize_clicked)

        ab_layout.addWidget(self.cat_header)
        ab_layout.addWidget(self.cat_count_lbl)
        ab_layout.addSpacing(20)
        ab_layout.addWidget(org_btn)
        ab_layout.addStretch()

        content.addWidget(action_box, stretch=2)
        layout.addLayout(content)

        self.refresh_categories()

    def refresh_categories(self):
        self.cat_list.clear()
        categories = [
            "People", "Animals", "Vehicles", "Technology", "Nature", "Food", 
            "Travel", "Sports", "Gaming", "Memes", "Funny", "Music", "Dance", 
            "Tutorials", "News", "Family", "Work", "Screenshots", "Miscellaneous"
        ]
        for c in categories:
            self.cat_list.addItem(c)

    def on_category_selected(self, cat_name: str):
        if not cat_name:
            return
        conn = self.db.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM videos WHERE category = ?;", (cat_name,)).fetchone()[0]
        self.cat_header.setText(f"Category: {cat_name}")
        self.cat_count_lbl.setText(f"Videos assigned to this category: {count}")

    def on_organize_clicked(self):
        cat_name = self.cat_list.currentItem().text() if self.cat_list.currentItem() else "Category"
        conn = self.db.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM videos WHERE category = ?;", (cat_name,)).fetchone()[0]
        
        dlg = OrganizationPreviewDialog(cat_name, count, self)
        if dlg.exec() == QDialog.Accepted and dlg.confirmed:
            QMessageBox.information(self, "Virtual Organization", f"Files for '{cat_name}' remain safe in their original location.")
