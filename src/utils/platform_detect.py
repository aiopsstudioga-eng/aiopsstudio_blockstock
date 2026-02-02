import platform
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"


def get_platform() -> Platform:
    """
    Detect the current platform.
    
    Returns:
        Platform: Always returns WINDOWS for this fork
    """
    return Platform.WINDOWS


def get_font_family() -> str:
    """
    Get the platform-appropriate font family.
    
    Returns:
        str: Font family name
    """
    return "Segoe UI"


def get_modifier_key() -> str:
    """
    Get the platform-appropriate modifier key for shortcuts.
    
    Returns:
        str: 'Ctrl' for Windows
    """
    return "Ctrl"


def should_use_native_menubar() -> bool:
    """
    Determine if native menu bar should be used.
    
    Returns:
        bool: Always False for Windows
    """
    return False
