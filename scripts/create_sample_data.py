#!/usr/bin/env python3
"""
Create sample data for testing reporting features.

This script populates the database with realistic sample transactions
to demonstrate the reporting capabilities.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.inventory_service import InventoryService


def create_sample_data():
    """Create sample inventory data."""
    print("=" * 60)
    print("Creating Sample Data for Reporting Tests")
    print("=" * 60)
    print()
    
    service = InventoryService()
    
    # Create some items if they don't exist
    print("Creating sample items...")
    
    items_to_create = [
        ("BEAN001", "Canned Black Beans", 1, 20),
        ("RICE001", "White Rice", 1, 50),
        ("PASTA001", "Spaghetti", 1, 30),
        ("SOUP001", "Tomato Soup", 1, 25),
        ("CEREAL001", "Corn Flakes", 1, 15),
    ]
    
    created_items = []
    for sku, name, cat_id, threshold in items_to_create:
        try:
            # Check if item exists
            existing = service.get_item_by_sku(sku)
            if existing:
                print(f"  ✓ {name} already exists")
                created_items.append(existing)
            else:
                item = service.create_item(sku, name, cat_id, reorder_threshold=threshold)
                print(f"  ✓ Created {name}")
                created_items.append(item)
        except Exception as e:
            print(f"  ✗ Error with {name}: {e}")
    
    print()
    print("Creating sample transactions...")
    
    # Create transactions over the past 30 days
    today = datetime.now()
    
    # Week 1: Initial purchases
    print("\n📅 Week 1: Initial Purchases")
    service.process_purchase(
        item_id=created_items[0].id,
        quantity=100,
        unit_cost_dollars=1.50,
        supplier="ABC Foods",
        notes="Initial stock purchase"
    )
    print("  ✓ Purchased 100 Canned Black Beans @ $1.50")
    
    service.process_purchase(
        item_id=created_items[1].id,
        quantity=200,
        unit_cost_dollars=0.75,
        supplier="ABC Foods",
        notes="Initial stock purchase"
    )
    print("  ✓ Purchased 200 lbs White Rice @ $0.75")
    
    service.process_purchase(
        item_id=created_items[2].id,
        quantity=75,
        unit_cost_dollars=1.25,
        supplier="Pasta Co",
        notes="Initial stock purchase"
    )
    print("  ✓ Purchased 75 boxes Spaghetti @ $1.25")
    
    # Week 2: Donations
    print("\n📅 Week 2: Donations Received")
    service.process_donation(
        item_id=created_items[0].id,
        quantity=50,
        fair_market_value_dollars=2.00,
        donor="Local Church",
        notes="Community food drive"
    )
    print("  ✓ Donated 50 Canned Black Beans (FMV: $2.00)")
    
    service.process_donation(
        item_id=created_items[3].id,
        quantity=100,
        fair_market_value_dollars=1.50,
        donor="Community Center",
        notes="Holiday donation"
    )
    print("  ✓ Donated 100 Tomato Soup (FMV: $1.50)")
    
    service.process_donation(
        item_id=created_items[4].id,
        quantity=40,
        fair_market_value_dollars=3.50,
        donor="Local Grocery Store",
        notes="Overstock donation"
    )
    print("  ✓ Donated 40 Corn Flakes (FMV: $3.50)")
    
    # Week 3: Client distributions
    print("\n📅 Week 3: Client Distributions")
    service.process_distribution(
        item_id=created_items[0].id,
        quantity=30,
        reason_code="CLIENT",
        notes="Family of 4"
    )
    print("  ✓ Distributed 30 Canned Black Beans to client")
    
    service.process_distribution(
        item_id=created_items[1].id,
        quantity=50,
        reason_code="CLIENT",
        notes="Family of 6"
    )
    print("  ✓ Distributed 50 lbs White Rice to client")
    
    service.process_distribution(
        item_id=created_items[2].id,
        quantity=20,
        reason_code="CLIENT",
        notes="Family of 3"
    )
    print("  ✓ Distributed 20 boxes Spaghetti to client")
    
    service.process_distribution(
        item_id=created_items[3].id,
        quantity=25,
        reason_code="CLIENT",
        notes="Senior citizen"
    )
    print("  ✓ Distributed 25 Tomato Soup to client")
    
    # Week 4: More purchases and mixed transactions
    print("\n📅 Week 4: Restocking & Mixed Transactions")
    service.process_purchase(
        item_id=created_items[1].id,
        quantity=100,
        unit_cost_dollars=0.80,
        supplier="ABC Foods",
        notes="Restock - price increase"
    )
    print("  ✓ Purchased 100 lbs White Rice @ $0.80 (price increased)")
    
    # Some spoilage
    service.process_distribution(
        item_id=created_items[3].id,
        quantity=5,
        reason_code="SPOILAGE",
        notes="Damaged cans"
    )
    print("  ✓ Recorded 5 Tomato Soup as spoilage")
    
    # Internal use
    service.process_distribution(
        item_id=created_items[4].id,
        quantity=3,
        reason_code="INTERNAL",
        notes="Staff training samples"
    )
    print("  ✓ Recorded 3 Corn Flakes as internal use")
    
    # More client distributions
    service.process_distribution(
        item_id=created_items[0].id,
        quantity=40,
        reason_code="CLIENT",
        notes="Family of 5"
    )
    print("  ✓ Distributed 40 Canned Black Beans to client")
    
    service.process_distribution(
        item_id=created_items[1].id,
        quantity=75,
        reason_code="CLIENT",
        notes="Large family"
    )
    print("  ✓ Distributed 75 lbs White Rice to client")
    
    print()
    print("=" * 60)
    print("✅ Sample Data Created Successfully!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • 5 inventory items created")
    print("  • 4 purchase transactions")
    print("  • 3 donation transactions")
    print("  • 9 distribution transactions")
    print("    - 6 client distributions")
    print("    - 1 spoilage")
    print("    - 2 internal use")
    print()
    print("You can now test the reporting features:")
    print("  1. Run: python src/main.py")
    print("  2. Navigate to Reports page")
    print("  3. Generate Financial Report (COGS)")
    print("  4. Generate Impact Report (FMV)")
    print("  5. Generate Stock Status Report")
    print()


if __name__ == "__main__":
    create_sample_data()
