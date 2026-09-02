import os
import sys
from pathlib import Path

# Add workspace root to Python path so package imports (ui, config, etc.) resolve correctly
workspace_root = Path(__file__).resolve().parents[1]
if str(workspace_root) not in sys.path:
    sys.path.append(str(workspace_root))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config.settings import settings
from logs.logger import logger

def main() -> None:
    # Ensure required directories exist
    for path in [settings.cache_dir, settings.logs_dir, settings.database_path.parent]:
        path.mkdir(parents=True, exist_ok=True)
    # Run migrations to ensure DB schema is present
    from database import migrations
    migrations.run_migrations()
    logger.info("Starting Local AI Video Analyzer")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
