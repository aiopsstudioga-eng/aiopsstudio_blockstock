
import sys
import os
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.item import InventoryItem
from services.inventory_service import InventoryService
from database.connection import get_db_manager

def verify_uom_removal():
    print("Verifying UOM Removal...")
    
    # 1. Check InventoryItem dataclass
    try:
        item = InventoryItem(
            sku="TEST001", 
            name="Test Item", 
            category_id=1, 
            quantity_on_hand=10
        )
        if hasattr(item, 'uom'):
            print("❌ FAILURE: InventoryItem still has 'uom' attribute")
            sys.exit(1)
        print("✅ InventoryItem model has no 'uom' attribute")
    except TypeError as e:
        print(f"❌ FAILURE: Could not instantiate InventoryItem: {e}")
        sys.exit(1)

    # 2. Check Service
    try:
        service = InventoryService(":memory:")
        # Utilize :memory: db for testing so we don't need init_db here
        # But wait, schema needs to be applied to memory db?
        # InventoryService usually expects a file or we need to init it.
        # Let's use get_db_manager and init it manually if needed.
        
        # Actually, let's just use the real init schema logic if possible or just mock it.
        # Simplest is to just check the method signature using introspection or try calling it.
        
        import inspect
        sig = inspect.signature(service.create_item)
        if 'uom' in sig.parameters:
            print("❌ FAILURE: create_item still has 'uom' parameter")
            sys.exit(1)
        print("✅ InventoryService.create_item signature is correct")
        
    except Exception as e:
        print(f"❌ FAILURE during service check: {e}")
        sys.exit(1)

    print("✅ Verification Successful!")

if __name__ == "__main__":
    verify_uom_removal()
