"""
Data service for importing and exporting data.
"""

import csv
import io
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path

from services.inventory_service import InventoryService
from models.item import InventoryItem
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataService:
    """Service for data import/export operations."""
    
    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service
        
    def export_items_to_csv(self, file_path: str) -> bool:
        """
        Export all items to CSV.
        
        Args:
            file_path: Destination file path
            
        Returns:
            bool: True if successful
        """
        try:
            items = self.inventory_service.get_all_items()
            categories = self.inventory_service.get_all_categories()
            category_map = {c.id: c.name for c in categories}
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    'ID', 'SKU', 'Name', 'Category', 'Quantity', 
                    'Unit Cost ($)', 'Total Value ($)', 'Reorder Threshold'
                ])
                
                # Data
                for item in items:
                    cat_name = category_map.get(item.category_id, "") if item.category_id else ""
                    writer.writerow([
                        item.id,
                        item.sku,
                        item.name,
                        cat_name,
                        item.quantity_on_hand,
                        item.current_unit_cost_dollars,
                        item.total_inventory_value_dollars,
                        item.reorder_threshold
                    ])
            return True
        except Exception as e:
            logger.error(f"Export error: {e}", exc_info=True)
            return False

    def import_items_from_csv(self, file_path: str) -> Tuple[int, int, List[str]]:
        """
        Import items from CSV.
        
        Expected Format: SKU, Name, Category ID, Reorder Threshold
        
        Args:
            file_path: Source file path
            
        Returns:
            Tuple[int, int, List[str]]: (Success Count, Fail Count, Error Messages)
        """
        success_count = 0
        fail_count = 0
        errors = []
        
        try:
            # Build category name -> id map for name-based resolution
            category_map = {}
            try:
                categories = self.inventory_service.get_all_categories()
                category_map = {c.name.upper(): c.id for c in categories}
            except Exception:
                logger.warning("Could not load categories for CSV import")

            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Normalize headers (strip whitespace, lowercase)
                reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
                
                required_fields = ['sku', 'name']
                for field in required_fields:
                    if field not in reader.fieldnames:
                        return 0, 0, [f"Missing required column: {field}"]
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        sku = row.get('sku', '').strip()
                        name = row.get('name', '').strip()
                        
                        if not sku or not name:
                            raise ValueError("SKU and Name are required")
                            
                        # Optional fields — resolve category by ID or name
                        category_id = self._resolve_category(row, category_map)
                        
                        threshold_str = row.get('reorder threshold', row.get('reorder_threshold', '10'))
                        reorder_threshold = int(threshold_str) if threshold_str.isdigit() else 10
                        
                        # New fields for Initial Stock
                        quantity_str = row.get('quantity', row.get('qty', row.get('quantity_on_hand', '0')))
                        # Remove commas/currency symbols if present
                        quantity_str = str(quantity_str).replace(',', '').strip()
                        quantity = float(quantity_str) if quantity_str and quantity_str.replace('.', '', 1).isdigit() else 0.0

                        cost_str = row.get('unit cost', row.get('unit_cost', row.get('unit cost ($)', row.get('cost', '0'))))
                        cost_str = str(cost_str).replace('$', '').replace(',', '').strip()
                        unit_cost = float(cost_str) if cost_str and cost_str.replace('.', '', 1).isdigit() else 0.0

                        # check if item exists
                        existing = self.inventory_service.get_item_by_sku(sku)
                        if existing:
                            # Update existing? For now, fail or skip.
                            # If user wants to update stock for existing items, that's a different feature (Stock Take)
                            fail_count += 1
                            errors.append(f"Row {row_num}: Item with SKU {sku} already exists")
                            continue
                            
                        # Create item
                        new_item = self.inventory_service.create_item(
                            sku=sku,
                            name=name,
                            category_id=category_id,
                            reorder_threshold=reorder_threshold
                        )
                        
                        # Add Initial Stock if Quantity > 0
                        if quantity > 0:
                            self.inventory_service.process_purchase(
                                item_id=new_item.id,
                                quantity=quantity,
                                unit_cost_dollars=unit_cost,
                                supplier="CSV Import",
                                notes="Initial import from file"
                            )

                        success_count += 1
                        
                    except Exception as e:
                        fail_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
                        
            return success_count, fail_count, errors
            
        except Exception as e:
            return 0, 0, [f"File error: {str(e)}"]

    def _resolve_category(self, row: Dict, category_map: Dict[str, int]) -> Optional[int]:
        """
        Resolve category from a CSV row.
        
        Checks for category ID first (columns: 'category id', 'category_id'),
        then falls back to category name lookup (column: 'category').
        If a category name is found that doesn't exist, a new category is created.
        
        Args:
            row: CSV row dict (lowercase keys)
            category_map: Mutable dict of {UPPER_NAME: id} for existing categories
            
        Returns:
            Category ID or None
        """
        # 1. Try integer category ID first
        category_id_str = row.get('category id', row.get('category_id', '')).strip()
        if category_id_str and category_id_str.isdigit():
            return int(category_id_str)
        
        # 2. Try category name lookup
        category_name = row.get('category', '').strip()
        if not category_name:
            return None
        
        upper_name = category_name.upper()
        if upper_name in category_map:
            return category_map[upper_name]
        
        # 3. Create new category
        try:
            db = self.inventory_service.db_manager
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO item_categories (name, description) VALUES (?, ?)",
                    (category_name, "Imported from CSV")
                )
                new_id = cursor.lastrowid
            
            category_map[upper_name] = new_id
            logger.info(f"Created new category during CSV import: '{category_name}' (id={new_id})")
            return new_id
        except Exception as e:
            logger.warning(f"Failed to create category '{category_name}': {e}")
            return None

    def export_transactions_to_csv(self, file_path: str) -> bool:
        """
        Export all transactions to CSV.
        """
        try:
            conn = self.inventory_service.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    t.id, t.transaction_date, t.transaction_type, 
                    i.sku, i.name as item_name,
                    t.quantity_change, t.unit_cost_cents, t.total_financial_impact_cents,
                    t.reason_code, t.supplier, t.donor, t.notes
                FROM inventory_transactions t
                JOIN inventory_items i ON t.item_id = i.id
                ORDER BY t.transaction_date DESC
            """)
            
            rows = cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Date', 'Type', 'SKU', 'Item', 
                    'Quantity', 'Unit Cost ($)', 'Total Impact ($)',
                    'Reason', 'Supplier', 'Donor', 'Notes'
                ])
                
                for row in rows:
                    writer.writerow([
                        row['id'],
                        row['transaction_date'],
                        row['transaction_type'],
                        row['sku'],
                        row['item_name'],
                        row['quantity_change'],
                        (row['unit_cost_cents'] or 0) / 100.0,
                        (row['total_financial_impact_cents'] or 0) / 100.0,
                        row['reason_code'],
                        row['supplier'],
                        row['donor'],
                        row['notes']
                    ])
            return True
        except Exception as e:
            logger.error(f"Export error: {e}", exc_info=True)
            return False
