"""
ATK Video AI Organizer - Centralized Logging System
Logs to logs/application.log, logs/analysis.log, and logs/errors.log
"""

import os
import logging
from logging.handlers import RotatingFileHandler

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        file_path = os.path.join(LOGS_DIR, filename)
        handler = RotatingFileHandler(file_path, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger

app_logger = setup_logger("app", "application.log")
analysis_logger = setup_logger("analysis", "analysis.log")
error_logger = setup_logger("error", "errors.log", level=logging.ERROR)
