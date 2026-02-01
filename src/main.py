#!/usr/bin/env python3
"""
Main entry point for AIOps Studio - Inventory application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


import os
from database.connection import init_database

def resolve_path(relative_path):
    """
    Resolve path for both development and PyInstaller environments.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = Path(__file__).parent.parent

    return os.path.join(base_path, relative_path)

def main():
    """Run the application."""
    # Ensure database exists
    db_path = "inventory.db"  # Created in CWD
    
    if not os.path.exists(db_path):
        print("Initializing database...")
        # Determine schema path
        if hasattr(sys, '_MEIPASS'):
             # In frozen app, schema is in src/database/schema.sql relative to bundle
             schema_path = os.path.join(sys._MEIPASS, 'src', 'database', 'schema.sql')
        else:
             # In dev, schema is relative to source
             schema_path = Path(__file__).parent / "database" / "schema.sql"
             
        try:
            init_database(db_path, str(schema_path))
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("AIOps Studio - Inventory")
    app.setOrganizationName("AIOps Studio")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
