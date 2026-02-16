"""
Centralized logging configuration for AIOps Studio - Inventory.

Provides application-wide logging with:
- File output with rotation (10MB max, 5 backups)
- Console output for development
- Automatic log directory creation in AppData
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(name: str = "AIOpsStudio") -> logging.Logger:
    """
    Configure application-wide logger with file and console output.
    
    Logs are saved to: C:\\Users\\<user>\\AppData\\Local\\AIOpsStudio\\logs\\
    
    Args:
        name: Logger name (typically __name__ from calling module)
        
    Returns:
        Configured logger instance
    """
    from utils.app_paths import get_app_data_dir
    
    # Create logs directory
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "aiopsstudio.log"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if already configured
    if logger.handlers:
        return logger
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter with detailed information
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_log_file_path() -> Path:
    """
    Get the path to the current log file.
    
    Returns:
        Path to aiopsstudio.log
    """
    from utils.app_paths import get_app_data_dir
    return get_app_data_dir() / "logs" / "aiopsstudio.log"
