"""
ATK Video AI Organizer - Main Application Entry Point & CLI Runner
Supports both Desktop GUI launcher and CLI commands (scan, analyze, search, duplicates, export, repair).
"""

import sys
import os
import argparse
import traceback

# ── PyInstaller frozen-exe compatibility ──────────────────────────────────────
# When running as a packed EXE, bundled data lives under sys._MEIPASS.
# When running as plain Python, use the directory that contains app.py.
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS          # temporary extraction dir inside the EXE
    APP_DIR  = os.path.dirname(sys.executable)  # folder where the .exe lives
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# Ensure root directory is in sys.path
sys.path.insert(0, BASE_DIR)

# Writable data / log directories next to the exe (or source root in dev)
DATA_DIR = os.path.join(APP_DIR, "data")
LOGS_DIR = os.path.join(APP_DIR, "logs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

from backend.hardware.gpu_detector import HardwareDetector
from backend.database.db_manager import DatabaseManager
from backend.pipeline.processor import PipelineProcessor
from backend.watcher.folder_watcher import LocalFolderWatcher


def _write_crash(exc: Exception) -> None:
    """Write a crash report next to the EXE so the user can read it."""
    crash_path = os.path.join(LOGS_DIR, "crash.log")
    with open(crash_path, "w", encoding="utf-8") as f:
        f.write("ATK Video AI Organizer – Crash Report\n")
        f.write("=" * 60 + "\n")
        traceback.print_exc(file=f)
    # Also try to show a Qt message box if Qt is available
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        _app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("ATK Video AI Organizer – Startup Error")
        msg.setText(f"The application crashed on startup.\n\nError: {exc}\n\nSee: {crash_path}")
        msg.exec()
    except Exception:
        pass


def run_gui():
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        # Print Hardware Banner
        detector = HardwareDetector()
        detector.print_startup_banner()

        app = QApplication(sys.argv)

        # Load Dark QSS Theme – use BASE_DIR which resolves correctly in frozen exe
        qss_path = os.path.join(BASE_DIR, "ui", "styles", "dark_theme.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())

        # Use writable APP_DIR for database (next to exe, not inside MEIPASS temp)
        db_path = os.path.join(DATA_DIR, "atk_video_organizer.db")
        db = DatabaseManager(db_path)
        processor = PipelineProcessor(db)
        processor.start()

        watcher = LocalFolderWatcher(db)
        watcher.start()

        window = MainWindow(db, processor, watcher)
        window.show()

        ret = app.exec()
        processor.stop()
        watcher.stop()
        sys.exit(ret)
    except Exception as exc:
        _write_crash(exc)
        sys.exit(1)

def run_cli():
    parser = argparse.ArgumentParser(description="ATK Video AI Organizer CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for video files")
    scan_parser.add_argument("folder", help="Directory path to scan")

    # analyze
    subparsers.add_parser("analyze", help="Run AI analysis on queued videos")

    # search
    search_parser = subparsers.add_parser("search", help="Search the video AI database")
    search_parser.add_argument("query", help="Search query string")

    # duplicates
    subparsers.add_parser("duplicates", help="Scan for exact and near duplicate videos")

    # export
    export_parser = subparsers.add_parser("export", help="Export metadata to JSON")
    export_parser.add_argument("--out", default="data/export.json", help="Output JSON path")

    args = parser.parse_args()

    if not args.command:
        run_gui()
        return

    db = DatabaseManager()
    detector = HardwareDetector()
    detector.print_startup_banner()

    if args.command == "scan":
        folder = os.path.abspath(args.folder)
        print(f"[CLI] Scanning folder: {folder}")
        from backend.pipeline.metadata import MetadataExtractor
        added = 0
        for root, _, files in os.walk(folder):
            for f in files:
                fp = os.path.join(root, f)
                if MetadataExtractor.is_supported_video(fp):
                    meta = MetadataExtractor.extract_metadata(fp)
                    if meta:
                        vid_id = db.add_video(meta)
                        if vid_id:
                            added += 1
        print(f"[CLI] Successfully indexed {added} videos into database.")

    elif args.command == "analyze":
        print("[CLI] Starting background AI processing...")
        processor = PipelineProcessor(db)
        processor.start()
        print("[CLI] Processing active. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            processor.stop()

    elif args.command == "search":
        print(f"[CLI] Searching database for query: '{args.query}'")
        from backend.models.embedding_model import LocalEmbeddingGenerator
        from backend.search.vector_store import LocalVectorStore
        from backend.search.hybrid_search import HybridSearchEngine
        
        emb = LocalEmbeddingGenerator()
        vstore = LocalVectorStore(db)
        engine = HybridSearchEngine(db, emb, vstore)
        results = engine.search(args.query)
        print(f"[CLI] Found {len(results)} matches:")
        for r in results[:10]:
            print(f" - [{r['match_score']}%] {r['filename']} | Description: {r['ai_description']}")

    elif args.command == "duplicates":
        from backend.pipeline.duplicate_finder import DuplicateFinder
        finder = DuplicateFinder(db)
        groups = finder.find_all_duplicates()
        print(f"[CLI] Found {len(groups)} duplicate groups.")

    elif args.command == "export":
        import json
        videos = db.get_all_videos(limit=10000)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2)
        print(f"[CLI] Exported {len(videos)} videos to {args.out}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["scan", "analyze", "search", "duplicates", "export"]:
        run_cli()
    else:
        run_gui()
