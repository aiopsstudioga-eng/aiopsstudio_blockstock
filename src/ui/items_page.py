"""
Items management page for viewing and managing inventory items.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from services.inventory_service import InventoryService
from ui.item_dialog import ItemDialog


class NumericTableWidgetItem(QTableWidgetItem):
    """
    Table widget item that sorts numerically.
    """
    def __lt__(self, other):
        try:
            # Get the data stored in UserRole (the raw numeric value)
            # If not set, try to parse the text (stripping currency/commas)
            my_value = self.data(Qt.ItemDataRole.UserRole)
            other_value = other.data(Qt.ItemDataRole.UserRole)
            
            if my_value is None:
                return super().__lt__(other)
                
            return float(my_value) < float(other_value)
        except (ValueError, TypeError):
            return super().__lt__(other)


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
        self.active_filters = {}  # Store active filters: {column_index: filter_value}
        self.init_ui()
        self.load_items()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("BlockStock Items")
        title.setStyleSheet("font-size: 24pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Category Filter
        self.category_filter = QComboBox()
        self.category_filter.setPlaceholderText("Filter by Category")
        self.category_filter.setFixedWidth(200)
        self.category_filter.addItem("All Categories", None)
        # Categories will be populated in load_items or a separate method
        self.category_filter.currentIndexChanged.connect(self.filter_items)
        header_layout.addWidget(self.category_filter)

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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "SKU", "Name", "Category", "Quantity", 
            "Unit Cost", "Total Value", "Status"
        ])
        
        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)  # Enable Native Sorting
        
        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Double-click to edit
        self.table.doubleClicked.connect(self.edit_selected_item)
        
        # Single click to filter
        self.table.cellClicked.connect(self.on_cell_clicked)
        
        layout.addWidget(self.table)
        
        # Filter status label
        self.filter_label = QLabel("")
        self.filter_label.setStyleSheet("color: #3498db; font-style: italic; padding: 5px;")
        layout.addWidget(self.filter_label)
        
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
            # Turn off sorting while loading to improve performance
            self.table.setSortingEnabled(False)
            
            items = self.service.get_all_items()
            categories = self.service.get_all_categories()
            
            # Populate category filter if empty (except "All Categories")
            if self.category_filter.count() <= 1:
                for cat in categories:
                    self.category_filter.addItem(cat.name, cat.id)

            self.table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                # SKU
                self.table.setItem(row, 0, QTableWidgetItem(item.sku))
                
                # Name
                self.table.setItem(row, 1, QTableWidgetItem(item.name))
                
                # Category
                category_name = ""
                item_cat_id = item.category_id
                
                if item_cat_id:
                    for cat in categories:
                        if cat.id == item_cat_id:
                            category_name = cat.name
                            break
                self.table.setItem(row, 2, QTableWidgetItem(category_name))
                
                # Quantity - Use NumericTableWidgetItem
                qty_item = NumericTableWidgetItem(f"{item.quantity_on_hand:,.1f}")
                qty_item.setData(Qt.ItemDataRole.UserRole, item.quantity_on_hand) # Store raw value for sorting
                qty_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 3, qty_item)
                
                # UOM column removed
                
                # Unit Cost - Use NumericTableWidgetItem
                cost_item = NumericTableWidgetItem(f"${item.current_unit_cost_dollars:.2f}")
                cost_item.setData(Qt.ItemDataRole.UserRole, item.current_unit_cost_dollars) # Store raw value
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 4, cost_item)
                
                # Total Value - Use NumericTableWidgetItem
                value_item = NumericTableWidgetItem(f"${item.total_inventory_value_dollars:,.2f}")
                value_item.setData(Qt.ItemDataRole.UserRole, item.total_inventory_value_dollars) # Store raw value
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, 5, value_item)
                
                # Status
                status = "Low Stock" if item.is_below_threshold() else "OK"
                status_item = QTableWidgetItem(status)
                if item.is_below_threshold():
                    status_item.setForeground(QColor("#e74c3c"))
                else:
                    status_item.setForeground(QColor("#27ae60"))
                self.table.setItem(row, 6, status_item)
                
                # Store item ID in first column's UserRole for identification
                # Note: We need to use a different role or ensure we don't conflict with sorting data if we used column 0 for numeric sort (we don't here)
                # But actually, SKU is column 0 and strings sort fine.
                # However, let's store the ID in a custom role just to be safe or use UserRole + 1
                # Standard UserRole is 32 (0x0100).
                # To avoid conflict with NumericTableWidgetItem which uses UserRole for valid numeric columns (3, 5, 6),
                # we are safe to use UserRole on column 0 (SKU) as it is not a NumericTableWidgetItem.
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, item.id)
                
                # Also store category ID in the category column for easy filtering
                self.table.item(row, 2).setData(Qt.ItemDataRole.UserRole, item.category_id)

            self.table.setSortingEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load items: {e}")
    
    def filter_items(self):
        """Filter table rows based on search text, category selection, and active click filters."""
        search_text = self.search_input.text().lower()
        category_data = self.category_filter.currentData() # This returns the category ID or None

        for row in range(self.table.rowCount()):
            show_row = True
            
            # 1. Filter by Text (SKU or Name)
            if search_text:
                sku_item = self.table.item(row, 0)
                name_item = self.table.item(row, 1)
                text_match = (sku_item and search_text in sku_item.text().lower()) or \
                             (name_item and search_text in name_item.text().lower())
                if not text_match:
                    show_row = False
            
            # 2. Filter by Category dropdown (if not "All Categories")
            if show_row and category_data is not None:
                # We stored category_id in column 2 UserRole
                cat_item = self.table.item(row, 2)
                row_cat_id = cat_item.data(Qt.ItemDataRole.UserRole)
                
                # Handle case where item has no category (row_cat_id is None or 0)
                if row_cat_id != category_data:
                    show_row = False
            
            # 3. Filter by active click filters
            if show_row and self.active_filters:
                for col_index, filter_value in self.active_filters.items():
                    cell_item = self.table.item(row, col_index)
                    if cell_item and cell_item.text() != filter_value:
                        show_row = False
                        break

            self.table.setRowHidden(row, not show_row)
    
    def on_cell_clicked(self, row: int, column: int):
        """Handle cell click to filter by that column's value."""
        # Skip if clicking on a hidden row
        if self.table.isRowHidden(row):
            return
        
        cell_item = self.table.item(row, column)
        if not cell_item:
            return
        
        filter_value = cell_item.text()
        
        # If this column is already filtered with this value, clear the filter
        if column in self.active_filters and self.active_filters[column] == filter_value:
            del self.active_filters[column]
        else:
            # Set filter for this column
            self.active_filters[column] = filter_value
        
        # Update filter label
        self.update_filter_label()
        
        # Apply filters
        self.filter_items()
    
    def update_filter_label(self):
        """Update the filter status label."""
        if not self.active_filters:
            self.filter_label.setText("")
            return
        
        column_names = ["SKU", "Name", "Category", "Quantity", "Unit Cost", "Total Value", "Status"]
        filter_texts = []
        
        for col_index, filter_value in self.active_filters.items():
            col_name = column_names[col_index] if col_index < len(column_names) else f"Column {col_index}"
            filter_texts.append(f"{col_name}: '{filter_value}'")
        
        self.filter_label.setText(f"🔍 Active Filters: {', '.join(filter_texts)} (Click cell again to clear)")
    
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
        
        # Start looking for ID from column 0
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
