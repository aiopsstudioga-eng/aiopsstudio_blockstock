"""
Example usage of AIOps Studio - Inventory Service.

Demonstrates common workflows including handling expiration and shrinkage.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from services.inventory_service import InventoryService
from models.transaction import ReasonCode
from database.connection import init_database


def main():
    """Demonstrate inventory service usage."""
    
    # Initialize database
    print("Initializing example database...")
    init_database("example_inventory.db")
    print()
    
    # Initialize service
    service = InventoryService("example_inventory.db")
    
    print("=" * 60)
    print("AIOps Studio - Inventory Service Examples")
    print("=" * 60)
    print()
    
    # Example 1: Create an item
    print("1. Creating item 'Canned Beans'...")
    item = service.create_item(
        sku="BEAN001",
        name="Canned Beans",
        category_id=3,  # Canned Goods
        uom="Can",
        reorder_threshold=20
    )
    print(f"   ✅ Created: {item}")
    print()
    
    # Example 2: Purchase inventory
    print("2. Purchasing 100 cans @ $1.50/can...")
    item, transaction = service.process_purchase(
        item_id=item.id,
        quantity=100,
        unit_cost_dollars=1.50,
        supplier="ABC Foods",
        notes="Initial stock"
    )
    print(f"   ✅ Inventory: {item.quantity_on_hand} cans")
    print(f"   ✅ Unit Cost: ${item.current_unit_cost_dollars:.2f}")
    print(f"   ✅ Total Value: ${item.total_inventory_value_dollars:.2f}")
    print()
    
    # Example 3: Receive donation
    print("3. Receiving donation of 50 cans (FMV $1.50/can)...")
    item, transaction = service.process_donation(
        item_id=item.id,
        quantity=50,
        fair_market_value_dollars=1.50,
        donor="Local Church",
        notes="Weekly donation"
    )
    print(f"   ✅ Inventory: {item.quantity_on_hand} cans")
    print(f"   ✅ Unit Cost: ${item.current_unit_cost_dollars:.2f} (reduced by donation)")
    print(f"   ✅ Total Value: ${item.total_inventory_value_dollars:.2f}")
    print()
    
    # Example 4: Distribute to clients
    print("4. Distributing 50 cans to clients...")
    item, transaction = service.process_distribution(
        item_id=item.id,
        quantity=50,
        reason_code=ReasonCode.CLIENT.value,
        notes="Family distributions"
    )
    print(f"   ✅ Inventory: {item.quantity_on_hand} cans")
    print(f"   ✅ COGS: ${transaction.total_financial_impact_dollars:.2f}")
    print()
    
    # Example 5: Handle expiration/shrinkage
    print("5. Removing 10 cans due to expiration (SPOILAGE)...")
    item, transaction = service.process_distribution(
        item_id=item.id,
        quantity=10,
        reason_code=ReasonCode.SPOILAGE.value,
        notes="Expired items - past best-by date"
    )
    print(f"   ✅ Inventory: {item.quantity_on_hand} cans")
    print(f"   ✅ COGS (loss): ${transaction.total_financial_impact_dollars:.2f}")
    print(f"   ✅ Reason: SPOILAGE")
    print()
    
    # Example 6: Handle internal use
    print("6. Using 5 cans for internal purposes...")
    item, transaction = service.process_distribution(
        item_id=item.id,
        quantity=5,
        reason_code=ReasonCode.INTERNAL.value,
        notes="Staff meal program"
    )
    print(f"   ✅ Inventory: {item.quantity_on_hand} cans")
    print(f"   ✅ COGS: ${transaction.total_financial_impact_dollars:.2f}")
    print()
    
    # Example 7: View transaction history
    print("7. Transaction history:")
    transactions = service.get_item_transactions(item.id)
    for i, txn in enumerate(transactions, 1):
        print(f"   {i}. {txn.transaction_type.value}: {abs(txn.quantity_change)} cans")
        if txn.reason_code:
            print(f"      Reason: {txn.reason_code}")
        if txn.notes:
            print(f"      Notes: {txn.notes}")
    print()
    
    # Summary
    print("=" * 60)
    print("Final Inventory Summary:")
    print(f"  Item: {item.name} ({item.sku})")
    print(f"  Quantity: {item.quantity_on_hand} {item.uom}")
    print(f"  Unit Cost: ${item.current_unit_cost_dollars:.2f}")
    print(f"  Total Value: ${item.total_inventory_value_dollars:.2f}")
    print("=" * 60)
    print()
    print("✅ All examples completed successfully!")
    print()
    print("Note: Expiration and shrinkage are handled using:")
    print("  - reason_code='SPOILAGE' for expired/damaged items")
    print("  - This properly tracks COGS and maintains audit trail")


if __name__ == "__main__":
    main()
