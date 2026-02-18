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
from services.data_service import DataService

CSV_FILE = "BLOCK STOCK.csv"

def import_csv():
    if not os.path.exists(CSV_FILE):
        print(f"❌ File '{CSV_FILE}' not found.")
        return

    print(f"Importing items from '{CSV_FILE}'...")
    
    try:
        # Initialize services
        # Note: InventoryService in this context needs a DB path if not using default
        # The default in InventoryService.__init__ is "inventory.db" which is correct for production
        service = InventoryService()
        data_service = DataService(service)
        
        success, fail, errors = data_service.import_items_from_csv(CSV_FILE)
        
        print("-" * 40)
        print(f"Import Complete.")
        print(f"Success: {success}")
        print(f"Failed:  {fail}")
        
        if errors:
            print("\nErrors:")
            for err in errors[:10]:
                print(f"  - {err}")
            if len(errors) > 10:
                print(f"  ...and {len(errors) - 10} more.")
                
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    import_csv()
