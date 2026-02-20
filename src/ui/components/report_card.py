"""
Report card component for the reports page.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QGraphicsDropShadowEffect, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class ReportCard(QWidget):
    """
    A styled card widget for displaying report options.
    """
    
    def __init__(self, title: str, description: str, icon: str, color: str, callback, parent=None):
        """
        Initialize the report card.
        
        Args:
            title: Title of the report
            description: Description of the report
            icon: Icon/Emoji for the report
            color: Accent color (hex string)
            callback: Function to call when generate button is clicked
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFixedSize(280, 240)  # Slightly larger for better spacing
        
        self.accent_color = color
        
        # Main Layout (no margins to allow shadow to be visible)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # Card Container (for shadow and border radius)
        self.container = QFrame()
        self.container.setObjectName("CardContainer")
        self.container.setStyleSheet(f"""
            QFrame#CardContainer {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                border-top: 5px solid {color};
            }}
        """)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))  # Subtle black shadow
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout.addWidget(self.container)
        
        # Content Layout inside the container
        content_layout = QVBoxLayout(self.container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        
        # Header (Icon + Title)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icon Container (New feature: visual separation)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 24pt; 
            color: {color};
            background-color: {self._lighten_color(color)};
            border-radius: 8px;
            padding: 5px;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(48, 48)
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI', sans-serif;
            font-size: 14pt; 
            font-weight: bold; 
            color: #2c3e50;
        """)
        header_layout.addWidget(title_label, 1) # Stretch factor 1
        
        content_layout.addLayout(header_layout)
        
        content_layout.addSpacing(5)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-family: 'Segoe UI', sans-serif;
            font-size: 10pt; 
            color: #7f8c8d; 
            line-height: 1.4;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(desc_label)
        
        # Spacer to push button to bottom
        content_layout.addStretch()
        
        # Button Container (for additional buttons)
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        
        # Generate Action Button
        self.btn = QPushButton("Generate Report")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_button_style(self.btn, color)
        self.btn.clicked.connect(callback)
        self.button_layout.addWidget(self.btn)
        
        content_layout.addLayout(self.button_layout)

    def _set_button_style(self, button: QPushButton, color: str):
        """Apply styles to a button."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, factor=1.2)};
            }}
        """)

    def _darken_color(self, hex_color: str, factor=0.8) -> str:
        """Darken a hex color."""
        # Simple lookup for known colors to avoid complex color math import dependency if possible
        # But robust enough to return input if unknown, or we could implement proper RGB scaling
        # For simplicity in this UI component, we'll use a mapping for improved visual consistency
        color_map = {
            "#3498db": "#2980b9", # Blue -> Dark Blue
            "#27ae60": "#219150", # Green -> Dark Green
            "#e67e22": "#d35400", # Orange -> Dark Orange
            "#9b59b6": "#8e44ad", # Purple -> Dark Purple
            "#16a085": "#138d75", # Teal -> Dark Teal
        }
        return color_map.get(hex_color, hex_color)

    def _lighten_color(self, hex_color: str) -> str:
        """Create a very light version of the color for icon background."""
        # Logic to return a transparent/light version
        # Using 10% opacity equivalent for light background
        # Since we can't easily do alpha with hex without potential issues on some Qt versions, 
        # let's use a very light grey or white for now, or specific mapping
        
        # Mapping to "tinted" backgrounds
        tint_map = {
            "#3498db": "#ebf5fb", # Light Blue
            "#27ae60": "#eafaf1", # Light Green
            "#e67e22": "#fdf2e9", # Light Orange
            "#9b59b6": "#f4ecf7", # Light Purple
            "#16a085": "#e8f8f5", # Light Teal
        }
        return tint_map.get(hex_color, "#f8f9fa")
        
    def add_extra_button(self, text: str, callback, color: str = None):
        """
        Add a second button to the card (e.g., 'Today').
        
        Args:
            text: Button text
            callback: Click handler
            color: Optional override color
        """
        # Rename original button to "Generate" if it was "Generate Report" to save space
        if self.btn.text() == "Generate Report":
            self.btn.setText("Generate")
            
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Use same accent color if none provided, or a secondary style
        btn_color = color if color else self.accent_color
        self._set_button_style(btn, btn_color)
        
        btn.clicked.connect(callback)
        self.button_layout.addWidget(btn)
