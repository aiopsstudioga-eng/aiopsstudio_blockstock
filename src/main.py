#!/usr/bin/env python3
"""
Main entry point for AIOps Studio - Inventory application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


import os
from database.connection import init_database, get_db_manager


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


class DatabaseSelectionDialog(QDialog):
    """Startup dialog to select database mode."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("AI OPS Studio - Select Mode")
        self.setFixedSize(450, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Select Database Mode")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Choose which database to use for this session:")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Training Mode Button
        training_btn = QPushButton("🎓 Training Mode")
        training_btn.setFixedHeight(60)
        training_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        training_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        training_btn.setToolTip("Use training.db - Safe for practice and demos")
        training_btn.clicked.connect(lambda: self.select_mode("training"))
        layout.addWidget(training_btn)
        
        training_desc = QLabel("Safe for practice • Demo data • No risk to real inventory")
        training_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        training_desc.setStyleSheet("color: #27ae60; font-size: 9pt;")
        layout.addWidget(training_desc)
        
        layout.addSpacing(10)
        
        # Production Mode Button
        production_btn = QPushButton("📦 Production Mode")
        production_btn.setFixedHeight(60)
        production_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        production_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        training_btn.setToolTip("Use inventory.db - Real inventory data")
        production_btn.clicked.connect(lambda: self.select_mode("production"))
        layout.addWidget(production_btn)
        
        production_desc = QLabel("Real inventory data • Use for actual operations")
        production_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        production_desc.setStyleSheet("color: #3498db; font-size: 9pt;")
        layout.addWidget(production_desc)
        
        layout.addStretch()
    
    def select_mode(self, mode: str):
        """Store selected mode and close dialog."""
        self.selected_mode = mode
        self.accept()


def get_schema_path():
    """Get the path to schema.sql."""
    if hasattr(sys, '_MEIPASS'):
        # In frozen app, schema is in src/database/schema.sql relative to bundle
        return os.path.join(sys._MEIPASS, 'src', 'database', 'schema.sql')
    else:
        # In dev, schema is relative to source
        return str(Path(__file__).parent / "database" / "schema.sql")


def setup_database(appdata_dir: str, db_name: str) -> str:
    """
    Set up the database, creating it if needed.
    
    Args:
        appdata_dir: AppData directory path
        db_name: Database filename (training.db or inventory.db)
    
    Returns:
        str: Full path to the database
    """
    db_path = os.path.join(appdata_dir, db_name)
    print(f"Using database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Initializing {db_name}...")
        schema_path = get_schema_path()
        try:
            init_database(db_path, schema_path)
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)
    
    return db_path


def main():
    """Run the application."""
    # Use AppData for database storage (Windows best practice)
    appdata_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'AIOpsStudio')
    
    # Create AppData directory if it doesn't exist
    os.makedirs(appdata_dir, exist_ok=True)
    
    # Create application first (needed for dialogs)
    app = QApplication(sys.argv)
    app.setApplicationName("AIOps Studio - Inventory")
    app.setOrganizationName("AIOps Studio")
    
    # Show database selection dialog
    selection_dialog = DatabaseSelectionDialog()
    if selection_dialog.exec() != QDialog.DialogCode.Accepted:
        # User closed the dialog without selecting
        sys.exit(0)
    
    # Determine which database to use
    if selection_dialog.selected_mode == "training":
        db_name = "training.db"
        mode_label = "TRAINING MODE"
    else:
        db_name = "inventory.db"
        mode_label = "PRODUCTION"
    
    # Set up the selected database
    db_path = setup_database(appdata_dir, db_name)
    
    # Initialize the global database manager singleton
    get_db_manager(db_path)
    print(f"Database manager initialized with: {db_path}")
    
    # Create and show main window with mode in title
    window = MainWindow()
    window.setWindowTitle(f"AI OPS Studio - [{mode_label}]")
    
    # Add visual indicator for training mode
    if selection_dialog.selected_mode == "training":
        # Store mode for potential UI indicators
        window.setProperty("database_mode", "training")
    else:
        window.setProperty("database_mode", "production")
    
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

