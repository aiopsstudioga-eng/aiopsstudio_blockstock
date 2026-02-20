"""
Item management dialog for creating and editing inventory items.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton,
    QMessageBox, QTabWidget, QWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from services.inventory_service import InventoryService
from models.item import InventoryItem
from models.transaction import TransactionType


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
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Item Details
        self.details_tab = QWidget()
        self.setup_details_tab()
        self.tabs.addTab(self.details_tab, "Item Details")
        
        # Tab 2: Transaction History (Only in edit mode)
        if self.is_edit_mode:
            self.history_tab = QWidget()
            self.setup_history_tab()
            self.tabs.addTab(self.history_tab, "Transaction History")

        # Buttons Setup (Common)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Close" if self.is_edit_mode else "Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Item")
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
            
    def setup_details_tab(self):
        """Setup the item details form."""
        layout = QVBoxLayout(self.details_tab)
        
        # Form layout
        form = QFormLayout()
        form.setSpacing(15)
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("e.g., BEAN001")
        if self.is_edit_mode:
            self.sku_input.setReadOnly(True)
        form.addRow("SKU*:", self.sku_input)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Canned Beans")
        form.addRow("Name*:", self.name_input)
        
        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form.addRow("Category:", self.category_combo)
        
        # Reorder Threshold
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 10000)
        self.threshold_spin.setValue(10)
        self.threshold_spin.setSuffix(" units")
        form.addRow("Reorder Threshold:", self.threshold_spin)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Buttons (Moved to bottom of main layout, or keep here? 
        # Better to have main action buttons at bottom of dialog, but history tab might not need save)
        # Let's keep Save/Cancel at the bottom of the DIALOG, outside tabs.

    def setup_history_tab(self):
        """Setup transaction history table."""
        layout = QVBoxLayout(self.history_tab)
        
        # Table
        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(8)
        self.tx_table.setHorizontalHeaderLabels([
            "Date", "Type", "Change", "Unit Cost", "Total Cost", "Reference", "Notes", "Void Info"
        ])
        self.tx_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tx_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.tx_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tx_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.tx_table)
        
        # Void Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.void_btn = QPushButton("Void Selected Transaction")
        self.void_btn.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        self.void_btn.clicked.connect(self.void_transaction)
        btn_layout.addWidget(self.void_btn)
        
        layout.addLayout(btn_layout)
        
        self.load_transactions()

    def load_transactions(self):
        """Load transactions for this item."""
        if not self.item:
            return
            
        transactions = self.service.get_item_transactions(self.item.id)
        # Sort by date desc
        # Sort by date desc (handle None dates safely)
        from datetime import datetime
        transactions.sort(key=lambda x: x.transaction_date or datetime.min, reverse=True)
        
        self.tx_table.setRowCount(len(transactions))
        
        for row, tx in enumerate(transactions):
            # Date
            date_str = tx.transaction_date.strftime("%Y-%m-%d %H:%M") if tx.transaction_date else ""
            self.tx_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Type
            type_str = tx.transaction_type.value
            if tx.transaction_type == TransactionType.CORRECTION:
                type_str = "CORRECTION"
            self.tx_table.setItem(row, 1, QTableWidgetItem(type_str))
            
            # Quantity Change
            qty_item = QTableWidgetItem(f"{tx.quantity_change:+.1f}")
            if tx.quantity_change > 0:
                qty_item.setForeground(QColor("green"))
            elif tx.quantity_change < 0:
                qty_item.setForeground(QColor("red"))
            self.tx_table.setItem(row, 2, qty_item)
            
            # Unit Cost
            if tx.transaction_type in (TransactionType.PURCHASE, TransactionType.DONATION):
                unit_cost_str = f"${tx.unit_cost_dollars:.2f}"
            else:
                unit_cost_str = "-"
            self.tx_table.setItem(row, 3, QTableWidgetItem(unit_cost_str))
            
            # Total Cost
            if tx.total_financial_impact_cents:
                total_cost_str = f"${tx.total_financial_impact_dollars:.2f}"
            else:
                total_cost_str = "-"
            self.tx_table.setItem(row, 4, QTableWidgetItem(total_cost_str))
            
            # Reference / Reason
            ref = tx.reason_code or tx.supplier or tx.donor or ""
            if tx.ref_transaction_id:
                ref += f" (Ref: #{tx.ref_transaction_id})"
            self.tx_table.setItem(row, 5, QTableWidgetItem(str(ref)))
            
            # Notes
            self.tx_table.setItem(row, 6, QTableWidgetItem(tx.notes or ""))
            
            # Void Info
            void_status = "VOIDED" if tx.is_voided else ""
            status_item = QTableWidgetItem(void_status)
            if tx.is_voided:
                status_item.setForeground(QColor("red"))
                status_item.setFont(QFont(self.font().family(), -1, QFont.Weight.Bold))
                
                # Strikeout entire row appearance (simulated)
                for col in range(7):
                    item = self.tx_table.item(row, col)
                    if item:
                        font = item.font()
                        font.setStrikeOut(True)
                        item.setFont(font)
                        item.setForeground(QColor("gray"))
                    
            self.tx_table.setItem(row, 7, status_item)
            
            # Store ID
            self.tx_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, tx.id)

    def void_transaction(self):
        """Void the selected transaction."""
        row = self.tx_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a transaction to void.")
            return
            
        tx_id = self.tx_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Check if already voided (visually)
        status_text = self.tx_table.item(row, 7).text()
        if status_text == "VOIDED":
            QMessageBox.warning(self, "Invalid Action", "This transaction is already voided.")
            return
            
        # Confirm
        from ui.void_dialog import VoidDialog
        dialog = VoidDialog(self, tx_id)
        if dialog.exec():
            reason = dialog.get_reason()
            try:
                self.service.void_transaction(tx_id, reason)
                QMessageBox.information(self, "Success", "Transaction voided successfully.")
                self.load_transactions() # Reload table
                # Also need to update parent (list view) since quantity changed
                # The accept() method will likely handle reload if we close, but we are staying open.
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

        
    
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
        if self.item.category_id:
            index = self.category_combo.findData(self.item.category_id)
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
