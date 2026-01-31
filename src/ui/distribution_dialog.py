"""
Distribution dialog for recording item distributions with reason codes.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

from services.inventory_service import InventoryService
from models.transaction import ReasonCode


class DistributionDialog(QDialog):
    """Dialog for recording distributions."""
    
    def __init__(self, service: InventoryService, parent=None):
        """
        Initialize distribution dialog.
        
        Args:
            service: InventoryService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.service = service
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Record Distribution")
        self.setMinimumWidth(550)
        
        # Orange/red theme for distributions
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel#header {
                background-color: #e67e22;
                color: white;
                padding: 20px;
                font-size: 18pt;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("📤 Distribution Entry")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Form container
        form_container = QVBoxLayout()
        form_container.setContentsMargins(30, 30, 30, 30)
        
        # Form
        form = QFormLayout()
        form.setSpacing(15)
        
        # Item selection
        self.item_combo = QComboBox()
        self.load_items()
        self.item_combo.currentIndexChanged.connect(self.update_available_quantity)
        form.addRow("Item*:", self.item_combo)
        
        # Available quantity display
        self.available_label = QLabel("0 units available")
        self.available_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        form.addRow("Available:", self.available_label)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" units")
        self.quantity_spin.valueChanged.connect(self.update_cogs)
        form.addRow("Quantity*:", self.quantity_spin)
        
        # Reason Code
        self.reason_combo = QComboBox()
        self.reason_combo.addItem("Client Distribution", ReasonCode.CLIENT.value)
        self.reason_combo.addItem("Spoilage/Expiration", ReasonCode.SPOILAGE.value)
        self.reason_combo.addItem("Internal Use", ReasonCode.INTERNAL.value)
        form.addRow("Reason*:", self.reason_combo)
        
        # COGS (calculated)
        self.cogs_label = QLabel("$0.00")
        self.cogs_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e67e22;")
        form.addRow("COGS (Cost):", self.cogs_label)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes (e.g., 'Family of 4', 'Expired items')...")
        self.notes_input.setMaximumHeight(80)
        form.addRow("Notes:", self.notes_input)
        
        form_container.addLayout(form)
        layout.addLayout(form_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 0, 30, 30)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Record Distribution")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_distribution)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Initialize displays
        self.update_available_quantity()
    
    def load_items(self):
        """Load items into combo box."""
        try:
            items = self.service.get_all_items()
            
            for item in items:
                self.item_combo.addItem(
                    f"{item.name} ({item.sku})",
                    item.id
                )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load items: {e}")
    
    def update_available_quantity(self):
        """Update available quantity display."""
        item_id = self.item_combo.currentData()
        if not item_id:
            self.available_label.setText("0 units available")
            return
        
        try:
            item = self.service.get_item(item_id)
            if item:
                self.available_label.setText(
                    f"{item.quantity_on_hand:,.1f} {item.uom} available"
                )
                self.update_cogs()
        except Exception as e:
            self.available_label.setText("Error loading quantity")
    
    def update_cogs(self):
        """Update COGS display."""
        item_id = self.item_combo.currentData()
        if not item_id:
            self.cogs_label.setText("$0.00")
            return
        
        try:
            item = self.service.get_item(item_id)
            if item:
                quantity = self.quantity_spin.value()
                cogs = quantity * item.current_unit_cost_dollars
                self.cogs_label.setText(f"${cogs:,.2f}")
        except Exception as e:
            self.cogs_label.setText("Error")
    
    def save_distribution(self):
        """Save distribution transaction."""
        item_id = self.item_combo.currentData()
        if not item_id:
            QMessageBox.warning(self, "Validation Error", "Please select an item")
            return
        
        quantity = self.quantity_spin.value()
        reason_code = self.reason_combo.currentData()
        notes = self.notes_input.toPlainText().strip() or None
        
        # Validate sufficient inventory
        try:
            item = self.service.get_item(item_id)
            if not item.can_distribute(quantity):
                QMessageBox.warning(
                    self,
                    "Insufficient Inventory",
                    f"Cannot distribute {quantity} units.\n"
                    f"Only {item.quantity_on_hand} {item.uom} available."
                )
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to validate inventory: {e}")
            return
        
        # Confirm distribution
        reason_text = self.reason_combo.currentText()
        reply = QMessageBox.question(
            self,
            "Confirm Distribution",
            f"Record distribution of {quantity} units?\n\n"
            f"Item: {item.name}\n"
            f"Reason: {reason_text}\n"
            f"COGS: {self.cogs_label.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            item, transaction = self.service.process_distribution(
                item_id=item_id,
                quantity=quantity,
                reason_code=reason_code,
                notes=notes
            )
            
            QMessageBox.information(
                self,
                "Success",
                f"Distribution recorded!\n\n"
                f"Item: {item.name}\n"
                f"Remaining Quantity: {item.quantity_on_hand} {item.uom}\n"
                f"COGS: ${transaction.total_financial_impact_dollars:.2f}"
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record distribution: {e}")
