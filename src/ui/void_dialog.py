from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class VoidDialog(QDialog):
    """
    Dialog to confirm transaction voiding and capture reason.
    """
    
    def __init__(self, parent=None, transaction_id=None):
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.reason = ""
        
        self.setWindowTitle("Void Transaction")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"Voiding Transaction #{self.transaction_id}")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        # Warning
        warning_box = QLabel(
            "⚠️ This action cannot be undone.\n"
            "A compensating transaction will be created to reverse the effect."
        )
        warning_box.setStyleSheet("""
            background-color: #fff3cdc7; 
            color: #856404; 
            border: 1px solid #ffeeba;
            border-radius: 4px;
            padding: 10px;
        """)
        warning_box.setWordWrap(True)
        layout.addWidget(warning_box)
        
        # Reason Input
        layout.addWidget(QLabel("Reason for voiding (Required):"))
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("e.g. Data entry error, Returned to vendor...")
        layout.addWidget(self.reason_input)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.void_btn = QPushButton("Void Transaction")
        self.void_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        self.void_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(self.void_btn)
        
        layout.addLayout(btn_layout)
        
    def validate_and_accept(self):
        reason = self.reason_input.toPlainText().strip()
        if len(reason) < 5:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Please provide a valid reason (min 5 characters)."
            )
            return
            
        self.reason = reason
        self.accept()
    
    def get_reason(self) -> str:
        return self.reason
