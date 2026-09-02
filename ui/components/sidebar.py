"""
ATK Video AI Organizer - Navigation Sidebar Component
Provides navigation tabs and visible OFFLINE MODE indicator.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QFrame
from PySide6.QtCore import Signal, Qt

class NavigationSidebar(QWidget):
    navigation_changed = Signal(str)

    NAV_ITEMS = [
        ("dashboard", "📊  Dashboard"),
        ("import", "📥  Import Videos"),
        ("library", "🎬  Video Library"),
        ("search", "🔍  Semantic Search"),
        ("duplicates", "👯  Duplicates"),
        ("categories", "🏷️  Categories"),
        ("processing", "⚡  Processing Queue"),
        ("favorites", "⭐  Favorites"),
        ("settings", "⚙️  Settings"),
        ("privacy", "🔒  Privacy & Offline")
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarContainer")
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # App Title Header
        title = QLabel("ATK VIDEO AI")
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        # OFFLINE MODE Badge
        offline_badge = QLabel("🟢  100% OFFLINE MODE")
        offline_badge.setObjectName("OfflineBadge")
        offline_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(offline_badge)

        layout.addSpacing(15)

        # Navigation Buttons
        for route_id, label_text in self.NAV_ITEMS:
            btn = QPushButton(label_text)
            btn.setProperty("route", route_id)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("NavButton")
            btn.setMinimumHeight(40)
            
            # Connect signal
            btn.clicked.connect(lambda checked, r=route_id: self.navigation_changed.emit(r))

            self.button_group.addButton(btn)
            self.buttons[route_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Select Dashboard by default
        if "dashboard" in self.buttons:
            self.buttons["dashboard"].setChecked(True)

    def set_active_route(self, route_id: str):
        if route_id in self.buttons:
            self.buttons[route_id].setChecked(True)
