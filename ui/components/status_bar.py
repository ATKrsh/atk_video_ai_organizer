"""
ATK Video AI Organizer - System Status Bar
Displays GPU, VRAM, CUDA status, active processing mode, and model summary.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from backend.hardware.gpu_detector import HardwareDetector

class SystemStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.hardware = HardwareDetector()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 4, 15, 4)

        summary = self.hardware.get_summary()

        self.gpu_label = QLabel(f"GPU: {summary['gpu']} ({summary['vram_free']} free)")
        self.cuda_label = QLabel(f"CUDA: {summary['cuda']}")
        self.mode_label = QLabel(f"Mode: {summary['processing_mode']}")
        self.models_label = QLabel(f"Models: {summary['selected_models']}")
        self.offline_label = QLabel("🔒 Privacy: Local Storage Only (No Cloud APIs)")

        layout.addWidget(self.gpu_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.cuda_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.mode_label)
        layout.addWidget(QLabel("|"))
        layout.addWidget(self.models_label)
        layout.addStretch()
        layout.addWidget(self.offline_label)

    def update_vram_display(self, free_vram_gb: float):
        self.gpu_label.setText(f"GPU: {self.hardware.gpu_name} ({free_vram_gb} GB free)")
