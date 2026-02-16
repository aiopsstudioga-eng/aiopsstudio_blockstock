"""
cx_Freeze setup script for AIOps Studio - Inventory
=====================================================

This script builds the application as a Windows executable using cx_Freeze.
"""

from cx_Freeze import setup, Executable
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, "src")

# Build options
build_exe_options = {
    "excludes": [
        "tkinter",
        "test",
        "tests",
        "pytest",
        "IPython",
        "jupyter",
        "pdb",
    ],
    "include_files": [
        (os.path.join(src_dir, "database", "schema.sql"), os.path.join("src", "database", "schema.sql")),
        (os.path.join(script_dir, "resources"), "resources"),
    ],
    # Optimize level (2 = highest)
    "optimize": 2,
    # Name of the directory to build to
    "build_exe": "dist",
}

# Executable configuration
executables = [
    Executable(
        os.path.join(src_dir, "main.py"),
        base="GUI",
        target_name="AIOpsStudio.exe",
        icon=os.path.join(script_dir, "resources", "icons", "icon.ico"),
    )
]

setup(
    name="AIOpsStudio",
    version="1.0.0",
    description="AIOps Studio - Inventory Management System for Food Pantries",
    author="AIOps Studio Team",
    options={"build_exe": build_exe_options},
    executables=executables,
)
