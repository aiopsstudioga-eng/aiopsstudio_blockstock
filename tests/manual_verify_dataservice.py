"""
Manual verification script for DataService.
"""
import sys
import os
from pathlib import Path

# Setup path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.inventory_service import InventoryService
from services.data_service import DataService

def verify_dataservice():
    print("Initializing services...")
    # Use memory DB for safety and speed
    service = InventoryService(":memory:")
    
    # Init schema
    with open("src/database/schema.sql", "r") as f:
        service.db_manager.get_connection().executescript(f.read())
        
    data_service = DataService(service)
    
    print("\n--- Test 1: Export Empty DB ---")
    export_path = "test_export_empty.csv"
    if data_service.export_items_to_csv(export_path):
        print(f"Export successful: {export_path}")
        with open(export_path, 'r') as f:
            print(f"Content:\n{f.read()}")
        os.remove(export_path)
    else:
        print("Export failed!")

    print("\n--- Test 2: Import Items ---")
    import_csv_content = """sku,name,category,reorder threshold
TEST001,Test Item 1,,10
TEST002,Test Item 2,5,20
"""
    import_path = "test_import.csv"
    with open(import_path, "w") as f:
        f.write(import_csv_content)
        
    success, fail, errors = data_service.import_items_from_csv(import_path)
    print(f"Import Results -> Success: {success}, Fail: {fail}")
    if errors:
        print(f"Errors: {errors}")
        
    # Verify items in DB
    items = service.get_all_items()
    print(f"Items in DB: {len(items)}")
    for item in items:
        print(f" - {item}")

    print("\n--- Test 3: Export Populated DB ---")
    export_path_pop = "test_export_populated.csv"
    if data_service.export_items_to_csv(export_path_pop):
        print(f"Export successful: {export_path_pop}")
        with open(export_path_pop, 'r') as f:
            content = f.read()
            print(f"Content:\n{content}")
            
            # Verify category name presence
            if "Dry Goods" in content:
                print("✅ Category Name 'Dry Goods' found in export")
            else:
                print("❌ Category Name 'Dry Goods' NOT found in export")
                
        os.remove(export_path_pop)
    
    # Cleanup
    if os.path.exists(import_path):
        os.remove(import_path)

if __name__ == "__main__":
    verify_dataservice()
