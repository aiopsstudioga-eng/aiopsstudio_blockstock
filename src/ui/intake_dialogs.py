"""
Intake dialogs for purchases and donations with color-coded UI.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from services.inventory_service import InventoryService


class PurchaseDialog(QDialog):
    """Dialog for recording purchases (BLUE theme)."""
    
    def __init__(self, service: InventoryService, parent=None):
        """
        Initialize purchase dialog.
        
        Args:
            service: InventoryService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.service = service
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Record Purchase")
        self.setMinimumWidth(550)
        
        # Blue theme for purchases
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel#header {
                background-color: #3498db;
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
        header = QLabel("💰 Purchase Entry")
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
        form.addRow("Item*:", self.item_combo)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" units")
        form.addRow("Quantity*:", self.quantity_spin)
        
        # Unit Cost
        self.unit_cost_spin = QDoubleSpinBox()
        self.unit_cost_spin.setRange(0.00, 100000)
        self.unit_cost_spin.setDecimals(2)
        self.unit_cost_spin.setPrefix("$")
        self.unit_cost_spin.valueChanged.connect(self.update_total)
        form.addRow("Unit Cost*:", self.unit_cost_spin)
        
        # Total Cost (calculated)
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #3498db;")
        form.addRow("Total Cost:", self.total_label)
        
        # Supplier dropdown
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItems([
            "Dollar Tree",
            "Restaurant Depot", 
            "Sam's Club",
            "Walmart",
            "Other"
        ])
        self.supplier_combo.setEditable(True)
        self.supplier_combo.lineEdit().setPlaceholderText("Select or type supplier...")
        form.addRow("Supplier:", self.supplier_combo)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
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
        
        save_btn = QPushButton("Record Purchase")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_purchase)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_items(self):
        """Load items into combo box."""
        try:
            items = self.service.get_all_items()
            
            for item in items:
                self.item_combo.addItem(
                    f"{item.name} ({item.sku}) - {item.quantity_on_hand:.1f} in stock",
                    item.id
                )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load items: {e}")
    
    def update_total(self):
        """Update total cost display."""
        quantity = self.quantity_spin.value()
        unit_cost = self.unit_cost_spin.value()
        total = quantity * unit_cost
        self.total_label.setText(f"${total:,.2f}")
    
    def save_purchase(self):
        """Save purchase transaction."""
        item_id = self.item_combo.currentData()
        if not item_id:
            QMessageBox.warning(self, "Validation Error", "Please select an item")
            return
        
        quantity = self.quantity_spin.value()
        unit_cost = self.unit_cost_spin.value()
        supplier = self.supplier_combo.currentText().strip() or None
        notes = self.notes_input.toPlainText().strip() or None
        
        try:
            item, transaction = self.service.process_purchase(
                item_id=item_id,
                quantity=quantity,
                unit_cost_dollars=unit_cost,
                supplier=supplier,
                notes=notes
            )
            
            QMessageBox.information(
                self,
                "Success",
                f"Purchase recorded!\n\n"
                f"Item: {item.name}\n"
                f"New Quantity: {item.quantity_on_hand:.1f}\n"
                f"New Unit Cost: ${item.current_unit_cost_dollars:.2f}"
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record purchase: {e}")


class DonationDialog(QDialog):
    """Dialog for recording donations (GREEN theme)."""
    
    def __init__(self, service: InventoryService, parent=None):
        """
        Initialize donation dialog.
        
        Args:
            service: InventoryService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.service = service
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Record Donation")
        self.setMinimumWidth(550)
        
        # Green theme for donations
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel#header {
                background-color: #27ae60;
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
        header = QLabel("🎁 Donation Entry")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Form container
        form_container = QVBoxLayout()
        form_container.setContentsMargins(30, 30, 30, 30)
        
        # Info message
        info = QLabel("💡 Donations are recorded at $0 cost but track fair market value for impact reporting")
        info.setWordWrap(True)
        info.setStyleSheet("background-color: #d5f4e6; padding: 10px; border-radius: 4px; color: #27ae60;")
        form_container.addWidget(info)
        
        form_container.addSpacing(20)
        
        # Form
        form = QFormLayout()
        form.setSpacing(15)
        
        # Item selection
        self.item_combo = QComboBox()
        self.load_items()
        form.addRow("Item*:", self.item_combo)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" units")
        form.addRow("Quantity*:", self.quantity_spin)
        
        # Fair Market Value
        self.fmv_spin = QDoubleSpinBox()
        self.fmv_spin.setRange(0.00, 100000)
        self.fmv_spin.setDecimals(2)
        self.fmv_spin.setPrefix("$")
        self.fmv_spin.valueChanged.connect(self.update_total)
        form.addRow("Fair Market Value (per unit):", self.fmv_spin)
        
        # Total FMV (calculated)
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #27ae60;")
        form.addRow("Total Impact Value:", self.total_label)
        
        # Donor
        self.donor_input = QLineEdit()
        self.donor_input.setPlaceholderText("e.g., Local Church")
        form.addRow("Donor:", self.donor_input)
        
        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
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
        
        save_btn = QPushButton("Record Donation")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_donation)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_items(self):
        """Load items into combo box."""
        try:
            items = self.service.get_all_items()
            
            for item in items:
                self.item_combo.addItem(
                    f"{item.name} ({item.sku}) - {item.quantity_on_hand:.1f} in stock",
                    item.id
                )
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load items: {e}")
    
    def update_total(self):
        """Update total FMV display."""
        quantity = self.quantity_spin.value()
        fmv = self.fmv_spin.value()
        total = quantity * fmv
        self.total_label.setText(f"${total:,.2f}")
    
    def save_donation(self):
        """Save donation transaction."""
        item_id = self.item_combo.currentData()
        if not item_id:
            QMessageBox.warning(self, "Validation Error", "Please select an item")
            return
        
        quantity = self.quantity_spin.value()
        fmv = self.fmv_spin.value()
        donor = self.donor_input.text().strip() or None
        notes = self.notes_input.toPlainText().strip() or None
        
        try:
            item, transaction = self.service.process_donation(
                item_id=item_id,
                quantity=quantity,
                fair_market_value_dollars=fmv,
                donor=donor,
                notes=notes
            )
            
            QMessageBox.information(
                self,
                "Success",
                f"Donation recorded!\n\n"
                f"Item: {item.name}\n"
                f"New Quantity: {item.quantity_on_hand:.1f}\n"
                f"New Unit Cost: ${item.current_unit_cost_dollars:.2f}\n"
                f"Impact Value: ${transaction.fair_market_value_dollars:.2f}"
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record donation: {e}")
