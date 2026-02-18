
import sys
import os
import csv
import shutil
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from services.inventory_service import InventoryService
from services.data_service import DataService
from database.connection import init_database

def test_csv_import():
    print("Testing CSV Import Logic...")
    
    test_dir = Path("csv_import_test")
    test_dir.mkdir(exist_ok=True)
    db_path = test_dir / "test_import.db"
    csv_path = test_dir / "import_data.csv"
    
    # 1. Setup DB
    if db_path.exists():
        os.remove(db_path)
    
    # Use schema from src
    schema_path = Path("src/database/schema.sql")
    init_database(str(db_path), str(schema_path))
    
    inv_service = InventoryService(str(db_path))
    data_service = DataService(inv_service)
    
    # 2. Create CSV File
    # Test typical headers including variations
    data = [
        ['SKU', 'Name', 'Category ID', 'Quantity', 'Unit Cost ($)'],
        ['TEST-001', 'Test Item 1', '1', '100', '5.50'],
        ['TEST-002', 'Test Item 2', '1', '50.5', '$10.00'], # Test currency symbol
        ['TEST-003', 'Test Item 3', '2', '0', '0'],         # Zero quantity
        ['TEST-004', 'Test Item 4', '2', '25', '2.00']
    ]
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
        
    print(f"Created CSV at {csv_path}")
    
    # 3. Import
    success, fail, errors = data_service.import_items_from_csv(str(csv_path))
    
    print(f"Import Result: Success={success}, Fail={fail}")
    if errors:
        print("Errors:", errors)
        
    if success != 4:
         print("FAIL: Expected 4 successes")
         return

    # 4. Verify Data
    # Item 1
    item1 = inv_service.get_item_by_sku('TEST-001')
    if item1 and item1.quantity_on_hand == 100.0 and item1.current_unit_cost_dollars == 5.50:
        print("PASS: Item 1 imported with correct quantity (100) and cost (5.50)")
    else:
        print(f"FAIL: Item 1 - Qty: {item1.quantity_on_hand}, Cost: {item1.current_unit_cost_dollars}")

    # Item 2 (Currency parsing)
    item2 = inv_service.get_item_by_sku('TEST-002')
    if item2 and item2.quantity_on_hand == 50.5 and item2.current_unit_cost_dollars == 10.00:
         print("PASS: Item 2 imported with correct quantity (50.5) and cost (10.00)")
    else:
         print(f"FAIL: Item 2 - Qty: {item2.quantity_on_hand}, Cost: {item2.current_unit_cost_dollars}")

    # Item 3 (Zero Qty)
    item3 = inv_service.get_item_by_sku('TEST-003')
    if item3 and item3.quantity_on_hand == 0:
         print("PASS: Item 3 imported with correct quantity (0)")
    else:
         print(f"FAIL: Item 3 - Qty: {item3.quantity_on_hand}")

if __name__ == "__main__":
    try:
        test_csv_import()
    finally:
        # Cleanup
        if os.path.exists("csv_import_test"):
            try:
                shutil.rmtree("csv_import_test")
                print("\nCleanup successful.")
            except Exception as e:
                print(f"Cleanup failed: {e}")
