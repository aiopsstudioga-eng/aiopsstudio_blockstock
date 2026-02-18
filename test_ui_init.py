
import sys
import os
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from ui.intake_dialogs import PurchaseDialog, DonationDialog
from services.inventory_service import InventoryService

def test_ui_init():
    app = QApplication(sys.argv)
    
    # Mock service
    class MockService:
        def get_all_items(self): return []
    
    service = MockService()
    
    print("Initializing PurchaseDialog...")
    try:
        dlg = PurchaseDialog(service)
        print("PurchaseDialog initialized successfully.")
    except Exception as e:
        print(f"FAILED to init PurchaseDialog: {e}")
        return

    print("Initializing DonationDialog...")
    try:
        dlg = DonationDialog(service)
        print("DonationDialog initialized successfully.")
    except Exception as e:
        print(f"FAILED to init DonationDialog: {e}")
        return

    print("UI Initialization Test Passed.")

if __name__ == "__main__":
    test_ui_init()
