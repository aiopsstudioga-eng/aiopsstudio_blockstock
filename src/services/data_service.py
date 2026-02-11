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
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow([
                    'ID', 'SKU', 'Name', 'Category', 'Quantity', 
                    'Unit Cost ($)', 'Total Value ($)', 'Reorder Threshold'
                ])
                
                # Data
                for item in items:
                    cat_name = "" # TODO: Fetch category name if needed, or just ID
                    writer.writerow([
                        item.id,
                        item.sku,
                        item.name,
                        item.category_id,
                        item.quantity_on_hand,
                        item.current_unit_cost_dollars,
                        item.total_inventory_value_dollars,
                        item.reorder_threshold
                    ])
            return True
        except Exception as e:
            print(f"Export error: {e}")
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
                            
                        # Optional fields
                        category_id_str = row.get('category id', row.get('category_id', ''))
                        category_id = int(category_id_str) if category_id_str and category_id_str.isdigit() else None
                        
                        threshold_str = row.get('reorder threshold', row.get('reorder_threshold', '10'))
                        reorder_threshold = int(threshold_str) if threshold_str.isdigit() else 10
                        
                        # check if item exists
                        existing = self.inventory_service.get_item_by_sku(sku)
                        if existing:
                            # Update existing? For now, skip or update basic info
                            # Let's simple skip for safety in MVP+, or maybe update name
                            fail_count += 1
                            errors.append(f"Row {row_num}: Item with SKU {sku} already exists")
                            continue
                            
                        # Create item
                        self.inventory_service.create_item(
                            sku=sku,
                            name=name,
                            category_id=category_id,
                            reorder_threshold=reorder_threshold
                        )
                        success_count += 1
                        
                    except Exception as e:
                        fail_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
                        
            return success_count, fail_count, errors
            
        except Exception as e:
            return 0, 0, [f"File error: {str(e)}"]

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
            print(f"Export error: {e}")
            return False
