"""
Error handling utilities for AIOps Studio - Inventory.

Provides consistent error handling with:
- User-friendly dialog boxes
- Automatic error logging
- Stack trace capture
"""

from PyQt6.QtWidgets import QMessageBox, QWidget
from typing import Optional
import logging


def show_error(
    parent: Optional[QWidget],
    title: str,
    message: str,
    exception: Optional[Exception] = None,
    log_level: str = "error"
) -> None:
    """
    Show error dialog to user AND log the error.
    
    Args:
        parent: Parent widget for dialog (can be None)
        title: Dialog title
        message: User-friendly error message
        exception: The exception object (optional, will log stack trace)
        log_level: 'error', 'warning', or 'critical'
    """
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
    
    # Log the error with full details
    if exception:
        log_msg = f"{message}: {str(exception)}"
        if log_level == "critical":
            logger.critical(log_msg, exc_info=True)
        elif log_level == "warning":
            logger.warning(log_msg, exc_info=True)
        else:
            logger.error(log_msg, exc_info=True)
    else:
        getattr(logger, log_level)(message)
    
    # Show user-friendly dialog
    if log_level == "critical":
        QMessageBox.critical(parent, title, message)
    elif log_level == "warning":
        QMessageBox.warning(parent, title, message)
    else:
        QMessageBox.critical(parent, title, message)


def show_info(parent: Optional[QWidget], title: str, message: str) -> None:
    """
    Show info dialog and log the message.
    
    Args:
        parent: Parent widget for dialog
        title: Dialog title
        message: Information message
    """
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
    
    logger.info(message)
    QMessageBox.information(parent, title, message)


def show_warning(parent: Optional[QWidget], title: str, message: str) -> None:
    """
    Show warning dialog and log the message.
    
    Args:
        parent: Parent widget for dialog
        title: Dialog title
        message: Warning message
    """
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
    
    logger.warning(message)
    QMessageBox.warning(parent, title, message)
