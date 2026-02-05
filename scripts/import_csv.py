#!/usr/bin/env python3
"""
Script to import inventory items from 'BLOCK STOCK.csv'.
"""

import sys
import csv
import os
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.inventory_service import InventoryService
from database.connection import get_db_manager

CSV_FILE = "BLOCK STOCK.csv"

def import_csv():
    if not os.path.exists(CSV_FILE):
        print(f"❌ File '{CSV_FILE}' not found.")
        return

    print(f"Importing items from '{CSV_FILE}'...")
    
    service = InventoryService()
    db = get_db_manager()
    
    # Cache existing categories to minimize DB lookups
    # Map name -> id
    existing_categories = {c.name.upper(): c.id for c in service.get_all_categories()}
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        
        # Skip specific header processing logic since the file structure is irregular
        # We will inspect each row
        
        row_num = 0
        for row in reader:
            row_num += 1
            
            # Row structure based on analysis:
            # Col 0: Empty (starts with comma)
            # Col 1: SKU
            # Col 2: Name
            # Col 3: Category
            # ...
            
            if len(row) < 4:
                continue
                
            sku = row[1].strip()
            name = row[2].strip()
            category_name = row[3].strip()
            
            # Skip header-like rows or empty rows
            if not sku or sku.upper() == "SKU":
                continue
                
            # Skip the weird row where category is "CATEGORY" (Line 2 in provided file)
            if category_name.upper() == "CATEGORY":
                # But wait, looking at line 2: 
                # ,SOUP-1RGCN,CANNED SOUP REGULAR,CATEGORY,...
                # It seems SOUP-1RGCN IS a valid SKU. 
                # And "CANNED SOUP REGULAR" IS a valid name.
                # But "CATEGORY" is not a valid category.
                # However, usually header rows don't have valid data in other columns.
                # Let's assume this is a header row artifact and skip it to be safe,
                # OR import it with a default category if it looks real.
                # "CANNED SOUP REGULAR" looks real. "CATEGORY" looks like a header label.
                # Let's map "CATEGORY" to None or "Uncategorized"?
                # Actually, looking at the file again:
                # Line 2: ...,SOUP-1RGCN... CATEGORY...
                # Line 3: ...,SOUP-1LGCN... MEAL...
                # It's highly likely Line 2 is just garbage/header mix. 
                # Safest to skip or import without category. 
                # Given "SOUP-1RGCN" looks like a real SKU that matches "SOUP-1LGCN", 
                # maybe I should try to import it.
                # But if Category is "CATEGORY", I'll put it in "Uncategorized" or leave blank.
                # Let's try to handle it.
                pass

            # Skip rows with empty SKU or Name (like the ones at the end of file)
            if not sku or not name:
                continue

            # Handle Category
            cat_id = None
            if category_name and category_name.upper() != "CATEGORY":
                upper_cat = category_name.upper()
                if upper_cat in existing_categories:
                    cat_id = existing_categories[upper_cat]
                else:
                    # Create new category
                    try:
                        print(f"  Creating new category: {category_name}")
                        # Insert directly using DB manager to avoid service complexity if needed,
                        # but service doesn't have create_category? Let's check.
                        # Reading inventory_service.py in previous turn... it only had get_all_categories.
                        # I strictly need to insert into item_categories.
                        
                        with db.transaction() as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO item_categories (name, description) VALUES (?, ?)", 
                                         (category_name, "Imported from CSV"))
                            cat_id = cursor.lastrowid
                            
                        existing_categories[upper_cat] = cat_id
                    except Exception as e:
                        print(f"  ⚠️ Failed to create category '{category_name}': {e}")
                        # Fallback to None
            
            try:
                # Check if item exists
                existing_item = service.get_item_by_sku(sku)
                if existing_item:
                    print(f"  Skipping existing SKU: {sku}")
                    skip_count += 1
                    continue
                
                # Create Item
                # Default reorder threshold to 10
                service.create_item(
                    sku=sku,
                    name=name,
                    category_id=cat_id,
                    reorder_threshold=10
                )
                print(f"  ✓ Imported: {sku} - {name}")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Error importing row {row_num} ({sku}): {e}")
                error_count += 1

    print("-" * 40)
    print(f"Import Complete.")
    print(f"Success: {success_count}")
    print(f"Skipped: {skip_count}")
    print(f"Errors:  {error_count}")

if __name__ == "__main__":
    import_csv()
