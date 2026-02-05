"""
Item management dialog for creating and editing inventory items.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt

from services.inventory_service import InventoryService
from models.item import InventoryItem


class ItemDialog(QDialog):
    """Dialog for creating/editing inventory items."""
    
    def __init__(self, service: InventoryService, item: InventoryItem = None, parent=None):
        """
        Initialize item dialog.
        
        Args:
            service: InventoryService instance
            item: InventoryItem to edit (None for new item)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.service = service
        self.item = item
        self.is_edit_mode = item is not None
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_item_data()
    
    def init_ui(self):
        """Initialize user interface."""
        title = "Edit Item" if self.is_edit_mode else "New Item"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(15)
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("e.g., BEAN001")
        if self.is_edit_mode:
            self.sku_input.setReadOnly(True)  # SKU cannot be changed
        form.addRow("SKU*:", self.sku_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Canned Beans")
        form.addRow("Name*:", self.name_input)
        
        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form.addRow("Category:", self.category_combo)
        
        # Unit of Measure removed
        
        # Reorder Threshold
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 10000)
        self.threshold_spin.setValue(10)
        self.threshold_spin.setSuffix(" units")
        form.addRow("Reorder Threshold:", self.threshold_spin)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_item)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def load_categories(self):
        """Load categories into combo box."""
        try:
            categories = self.service.get_all_categories()
            
            self.category_combo.addItem("(None)", None)
            
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load categories: {e}"
            )
    
    def load_item_data(self):
        """Load item data into form (edit mode)."""
        if not self.item:
            return
        
        self.sku_input.setText(self.item.sku)
        self.name_input.setText(self.item.name)
        
        # Set category
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        # UOM load removed
        
        self.threshold_spin.setValue(self.item.reorder_threshold)
    
    def save_item(self):
        """Save item."""
        # Validate
        sku = self.sku_input.text().strip()
        name = self.name_input.text().strip()
        
        if not sku:
            QMessageBox.warning(self, "Validation Error", "SKU is required")
            self.sku_input.setFocus()
            return
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required")
            self.name_input.setFocus()
            return
        
        
        category_id = self.category_combo.currentData()
        # uom = self.uom_combo.currentText() # removed
        threshold = self.threshold_spin.value()
        
        try:
            if self.is_edit_mode:
                # Update existing item
                self.service.update_item(
                    item_id=self.item.id,
                    name=name,
                    category_id=category_id,
                    # uom=uom,
                    reorder_threshold=threshold
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"Item '{name}' updated successfully!"
                )
            else:
                # Create new item
                self.service.create_item(
                    sku=sku,
                    name=name,
                    category_id=category_id,
                    # uom=uom,
                    reorder_threshold=threshold
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"Item '{name}' created successfully!"
                )
            
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save item: {e}")
