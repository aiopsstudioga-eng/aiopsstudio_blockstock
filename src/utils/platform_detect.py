"""
Platform detection utilities for cross-platform UI.

Detects the operating system and provides platform-specific configurations.
"""

import platform
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    UNKNOWN = "unknown"


def get_platform() -> Platform:
    """
    Detect the current platform.
    
    Returns:
        Platform: Current operating system
    """
    system = platform.system()
    
    if system == 'Darwin':
        return Platform.MACOS
    elif system == 'Windows':
        return Platform.WINDOWS
    elif system == 'Linux':
        return Platform.LINUX
    else:
        return Platform.UNKNOWN


def get_font_family() -> str:
    """
    Get the platform-appropriate font family.
    
    Returns:
        str: Font family name
    """
    current_platform = get_platform()
    
    if current_platform == Platform.MACOS:
        return "SF Pro"  # San Francisco
    elif current_platform == Platform.WINDOWS:
        return "Segoe UI"
    else:
        return "Arial"  # Fallback


def get_modifier_key() -> str:
    """
    Get the platform-appropriate modifier key for shortcuts.
    
    Returns:
        str: 'Ctrl' for Windows/Linux, 'Cmd' for macOS
    """
    current_platform = get_platform()
    
    if current_platform == Platform.MACOS:
        return "Cmd"
    else:
        return "Ctrl"


def should_use_native_menubar() -> bool:
    """
    Determine if native menu bar should be used.
    
    Returns:
        bool: True for macOS (global menu bar), False otherwise
    """
    return get_platform() == Platform.MACOS
