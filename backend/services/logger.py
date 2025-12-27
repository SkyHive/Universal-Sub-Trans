import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from appdirs import user_log_dir

def setup_logger(name: str = "universal-sub") -> logging.Logger:
    """
    Sets up a logger with both console and rotating file handlers.
    """
    logger = logging.getLogger(name)
    
    # Default level, will be updated by config_mgr
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # Log directory setup: local 'logs' folder
    # Detect root path without importing PlatformManager to avoid circular imports
    if getattr(sys, 'frozen', False):
        root = os.path.dirname(sys.executable)
    else:
        # File is at backend/services/logger.py, root is 3 levels up
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
    log_dir = os.path.join(root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(module)s:%(lineno)d)"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()
