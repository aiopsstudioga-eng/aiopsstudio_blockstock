"""
Items management page for viewing and managing inventory items.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from services.inventory_service import InventoryService
from ui.item_dialog import ItemDialog


class ItemsPage(QWidget):
    """Items management page."""
    
    def __init__(self, service: InventoryService, parent=None):
        """
        Initialize items page.
        
        Args:
            service: InventoryService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.service = service
        self.init_ui()
        self.load_items()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Inventory Items")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search items...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_items)
        header_layout.addWidget(self.search_input)
        
        # New item button
        new_btn = QPushButton("+ New Item")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_btn.clicked.connect(self.create_item)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "SKU", "Name", "Category", "Quantity", "UOM",
            "Unit Cost", "Total Value", "Status"
        ])
        
        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Double-click to edit
        self.table.doubleClicked.connect(self.edit_selected_item)
        
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_selected_item)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("color: #e74c3c;")
        delete_btn.clicked.connect(self.delete_selected_item)
        action_layout.addWidget(delete_btn)
        
        layout.addLayout(action_layout)
    
    def load_items(self):
        """Load items into table."""
        try:
            items = self.service.get_all_items()
            
            self.table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                # SKU
                self.table.setItem(row, 0, QTableWidgetItem(item.sku))
                
                # Name
                self.table.setItem(row, 1, QTableWidgetItem(item.name))
                
                # Category
                category_name = ""
                if item.category_id:
                    categories = self.service.get_all_categories()
                    for cat in categories:
                        if cat.id == item.category_id:
                            category_name = cat.name
                            break
                self.table.setItem(row, 2, QTableWidgetItem(category_name))
                
                # Quantity
                qty_item = QTableWidgetItem(f"{item.quantity_on_hand:,.1f}")
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 3, qty_item)
                
                # UOM
                self.table.setItem(row, 4, QTableWidgetItem(item.uom))
                
                # Unit Cost
                cost_item = QTableWidgetItem(f"${item.current_unit_cost_dollars:.2f}")
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 5, cost_item)
                
                # Total Value
                value_item = QTableWidgetItem(f"${item.total_inventory_value_dollars:,.2f}")
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 6, value_item)
                
                # Status
                status = "Low Stock" if item.is_below_threshold() else "OK"
                status_item = QTableWidgetItem(status)
                if item.is_below_threshold():
                    status_item.setForeground(QColor("#e74c3c"))
                else:
                    status_item.setForeground(QColor("#27ae60"))
                self.table.setItem(row, 7, status_item)
                
                # Store item ID in row data
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, item.id)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load items: {e}")
    
    def filter_items(self, text: str):
        """Filter table rows based on search text."""
        for row in range(self.table.rowCount()):
            show_row = False
            
            # Search in SKU and Name columns
            for col in [0, 1]:
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            
            self.table.setRowHidden(row, not show_row)
    
    def create_item(self):
        """Create new item."""
        dialog = ItemDialog(self.service, parent=self)
        if dialog.exec():
            self.load_items()
    
    def edit_selected_item(self):
        """Edit selected item."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit")
            return
        
        item_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        item = self.service.get_item(item_id)
        
        if item:
            dialog = ItemDialog(self.service, item, parent=self)
            if dialog.exec():
                self.load_items()
    
    def delete_selected_item(self):
        """Delete selected item."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete")
            return
        
        item_name = self.table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{item_name}'?\n\n"
            "This will soft-delete the item (preserve transaction history).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                item_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
                self.service.soft_delete_item(item_id)
                QMessageBox.information(self, "Success", f"Item '{item_name}' deleted")
                self.load_items()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {e}")
