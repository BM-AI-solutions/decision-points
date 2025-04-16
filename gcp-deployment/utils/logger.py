import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(
    name: str = 'decision_points',
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up application logger.

    Args:
        name: Logger name
        log_level: Override default log level
        log_file: Override default log file

    Returns:
        Configured logger instance
    """
    from config import Config

    # Get settings from config if not provided
    log_level = log_level or Config.LOG_LEVEL
    log_file = log_file or Config.LOG_FILE

    # Create logger
    logger = logging.getLogger(name)

    # Set level from string
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger