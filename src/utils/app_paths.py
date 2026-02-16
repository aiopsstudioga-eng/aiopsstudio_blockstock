"""
Application path utilities.

Provides centralized path management for AppData directories.
"""

import os
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Get the application's AppData directory.
    
    Returns:
        Path: Path to C:\\Users\\<username>\\AppData\\Local\\AIOpsStudio
    """
    appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    app_dir = Path(appdata) / 'AIOpsStudio'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_reports_dir() -> Path:
    """
    Get the reports directory in AppData.
    
    Returns:
        Path: Path to reports directory, created if it doesn't exist
    """
    reports_dir = get_app_data_dir() / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def get_backups_dir() -> Path:
    """
    Get the backups directory in AppData.
    
    Returns:
        Path: Path to backups directory, created if it doesn't exist
    """
    backups_dir = get_app_data_dir() / 'backups'
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def get_logs_dir() -> Path:
    """
    Get the logs directory in AppData.
    
    Returns:
        Path: Path to logs directory, created if it doesn't exist
    """
    logs_dir = get_app_data_dir() / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
