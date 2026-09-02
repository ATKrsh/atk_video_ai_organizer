"""
ATK Video AI Organizer - Local Filesystem Folder Watcher
Monitors user-designated video folders for new video additions using watchdog.
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.pipeline.metadata import MetadataExtractor
from backend.database.db_manager import DatabaseManager
from backend.utils.logger import app_logger, error_logger

class NewVideoEventHandler(FileSystemEventHandler):
    def __init__(self, db_manager: DatabaseManager, on_new_video_callback=None):
        super().__init__()
        self.db = db_manager
        self.callback = on_new_video_callback

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if MetadataExtractor.is_supported_video(file_path):
            app_logger.info(f"NEW VIDEO DETECTED by Folder Watcher: {file_path}")
            # Wait 1s for file write to complete
            time.sleep(1.0)
            meta = MetadataExtractor.extract_metadata(file_path)
            if meta:
                vid_id = self.db.add_video(meta)
                if vid_id and self.callback:
                    self.callback(file_path)

class LocalFolderWatcher:
    def __init__(self, db_manager: DatabaseManager, on_new_video_callback=None):
        self.db = db_manager
        self.callback = on_new_video_callback
        self.observer = Observer()
        self.watched_paths = set()

    def start(self):
        folders = self.db.get_watched_folders()
        for f in folders:
            path = f["folder_path"]
            self.add_folder_to_watch(path)

        self.observer.start()
        app_logger.info("Local Folder Watcher service started")

    def add_folder_to_watch(self, folder_path: str):
        if not os.path.exists(folder_path) or folder_path in self.watched_paths:
            return

        handler = NewVideoEventHandler(self.db, self.callback)
        self.observer.schedule(handler, path=folder_path, recursive=True)
        self.watched_paths.add(folder_path)
        self.db.add_watched_folder(folder_path)
        app_logger.info(f"Watching folder for new videos: {folder_path}")

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            app_logger.info("Local Folder Watcher service stopped")
