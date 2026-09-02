import sys
from PySide6.QtWidgets import QMainWindow, QTableView, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHeaderView
from PySide6.QtCore import Qt
from ui.library_model import LibraryModel
from services.library_service import LibraryService
from logs.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local AI Video Analyzer")
        self.resize(1000, 600)
        # Central widget layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        # Header / controls
        header = QWidget()
        header_layout = QVBoxLayout(header)
        self.add_folder_btn = QPushButton("Add Folder to Library")
        self.add_folder_btn.clicked.connect(self.on_add_folder)
        header_layout.addWidget(self.add_folder_btn)
        layout.addWidget(header)
        # Table view
        self.table = QTableView()
        self.model = LibraryModel()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        layout.addWidget(self.table)
        # Status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready")


    def on_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.status.showMessage(f"Scanning {folder} ...")
            try:
                added = LibraryService().add_path(folder)
                self.status.showMessage(f"Added {len(added)} videos")
                self.model.refresh()
            except Exception as e:
                logger.exception(f"Failed to add folder {folder}: {e}")
                self.status.showMessage(f"Error: {e}")
