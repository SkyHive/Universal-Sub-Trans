import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from appdirs import user_log_dir

def setup_logger(name: str = "universal-sub") -> logging.Logger:
    """
    Sets up a logger with both console and rotating file handlers,
    using JSON formatting for the file handler.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Log directory setup
    log_dir = user_log_dir("UniversalSub", "UniversalSub")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (JSON)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    json_formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(levelname)s %(name)s %(message)s %(module)s %(funcName)s"
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()
