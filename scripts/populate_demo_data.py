"""
Demo data population script for AI OPS Studio - Inventory.

Creates sample inventory items and transactions for demonstration purposes.
Run this script to populate a fresh database with realistic food pantry data.

Usage:
    python scripts/populate_demo_data.py
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import get_db_manager


def populate_demo_data(db_path: str):
    """
    Populate database with demo data.
    
    Args:
        db_path: Path to the database file
    """
    print(f"Populating demo data in: {db_path}")
    
    db_manager = get_db_manager(db_path)
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # =========================================================================
    # SAMPLE INVENTORY ITEMS
    # =========================================================================
    sample_items = [
        # Canned Goods (category_id=3)
        ("CAN-001", "Canned Corn", 3, 25, 50),
        ("CAN-002", "Canned Green Beans", 3, 25, 60),
        ("CAN-003", "Canned Tomatoes", 3, 20, 45),
        ("CAN-004", "Canned Tuna", 3, 15, 80),
        ("CAN-005", "Canned Soup - Chicken Noodle", 3, 30, 120),
        ("CAN-006", "Canned Soup - Tomato", 3, 25, 90),
        ("CAN-007", "Canned Fruit Cocktail", 3, 20, 55),
        ("CAN-008", "Canned Peaches", 3, 20, 40),
        
        # Dry Goods (category_id=4)
        ("DRY-001", "Rice - White 2lb", 4, 30, 100),
        ("DRY-002", "Pasta - Spaghetti", 4, 25, 150),
        ("DRY-003", "Pasta - Macaroni", 4, 25, 120),
        ("DRY-004", "Cereal - Corn Flakes", 4, 20, 75),
        ("DRY-005", "Oatmeal - Instant", 4, 25, 60),
        ("DRY-006", "Peanut Butter 16oz", 4, 15, 85),
        ("DRY-007", "Flour - All Purpose 5lb", 4, 20, 50),
        ("DRY-008", "Sugar - Granulated 4lb", 4, 20, 40),
        ("DRY-009", "Beans - Dried Black", 4, 30, 70),
        ("DRY-010", "Beans - Dried Pinto", 4, 30, 65),
        
        # Fresh Produce (category_id=5) - typically lower quantities
        ("FRS-001", "Apples - Red Delicious", 5, 10, 30),
        ("FRS-002", "Bananas", 5, 10, 25),
        ("FRS-003", "Oranges", 5, 10, 20),
        ("FRS-004", "Potatoes - Russet 5lb", 5, 15, 40),
        ("FRS-005", "Onions - Yellow", 5, 15, 35),
        
        # Frozen (category_id=6)
        ("FRZ-001", "Frozen Vegetables - Mixed", 6, 20, 50),
        ("FRZ-002", "Frozen Chicken Breast", 6, 10, 35),
        ("FRZ-003", "Frozen Ground Beef 1lb", 6, 10, 25),
        
        # Hygiene (category_id=7)
        ("HYG-001", "Toothpaste", 7, 25, 60),
        ("HYG-002", "Soap Bars - Pack of 4", 7, 20, 45),
        ("HYG-003", "Shampoo 12oz", 7, 20, 50),
        ("HYG-004", "Deodorant", 7, 20, 40),
        
        # Cleaning (category_id=8)
        ("CLN-001", "Dish Soap", 8, 25, 55),
        ("CLN-002", "Laundry Detergent", 8, 15, 30),
        ("CLN-003", "All-Purpose Cleaner", 8, 20, 35),
        
        # Paper Products (category_id=9)
        ("PAP-001", "Toilet Paper 4-pack", 9, 20, 80),
        ("PAP-002", "Paper Towels 2-pack", 9, 20, 60),
        ("PAP-003", "Facial Tissues", 9, 25, 45),
    ]
    
    print(f"Inserting {len(sample_items)} sample items...")
    
    for sku, name, category_id, threshold, initial_qty in sample_items:
        cursor.execute("""
            INSERT OR IGNORE INTO inventory_items 
            (sku, name, category_id, reorder_threshold, quantity_on_hand, total_cost_basis_cents, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (sku, name, category_id, threshold, initial_qty, 0))
    
    conn.commit()
    
    # =========================================================================
    # SAMPLE TRANSACTIONS (Purchases, Donations, Distributions)
    # =========================================================================
    print("Creating sample transactions...")
    
    # Get all items
    cursor.execute("SELECT id, name, sku, quantity_on_hand FROM inventory_items WHERE is_active = 1")
    items = cursor.fetchall()
    
    # Suppliers and Donors
    suppliers = ["ACME Foods", "Sysco", "US Foods", "Local Grocery Co", "Costco Business"]
    donors = ["First Baptist Church", "Community Foundation", "Food Drive 2026", "Anonymous", "Local Business Guild"]
    
    transaction_count = 0
    
    for item in items:
        item_id = item['id']
        item_name = item['name']
        initial_qty = item['quantity_on_hand']
        
        # Reset quantity to 0 first (we'll build it up with transactions)
        cursor.execute("UPDATE inventory_items SET quantity_on_hand = 0, total_cost_basis_cents = 0 WHERE id = ?", (item_id,))
        
        # Generate 2-4 intake transactions per item
        num_intakes = random.randint(2, 4)
        running_qty = 0
        running_cost = 0
        
        for i in range(num_intakes):
            # Random date in past 60 days
            days_ago = random.randint(1, 60)
            trans_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Randomly choose purchase or donation (70% purchase, 30% donation)
            if random.random() < 0.7:
                # PURCHASE
                qty = random.randint(10, 50)
                unit_cost_cents = random.randint(75, 500)  # $0.75 - $5.00
                total_cost = qty * unit_cost_cents
                supplier = random.choice(suppliers)
                
                cursor.execute("""
                    INSERT INTO inventory_transactions 
                    (item_id, transaction_type, quantity_change, unit_cost_cents, supplier, transaction_date)
                    VALUES (?, 'PURCHASE', ?, ?, ?, ?)
                """, (item_id, qty, unit_cost_cents, supplier, trans_date))
                
                running_qty += qty
                running_cost += total_cost
            else:
                # DONATION
                qty = random.randint(5, 30)
                fmv_cents = random.randint(100, 400) * qty  # Fair market value
                donor = random.choice(donors)
                
                cursor.execute("""
                    INSERT INTO inventory_transactions 
                    (item_id, transaction_type, quantity_change, unit_cost_cents, fair_market_value_cents, donor, transaction_date)
                    VALUES (?, 'DONATION', ?, 0, ?, ?, ?)
                """, (item_id, qty, fmv_cents, donor, trans_date))
                
                running_qty += qty
                # Donations don't add to cost basis
            
            transaction_count += 1
        
        # Generate 1-3 distributions per item
        num_distributions = random.randint(1, 3)
        for i in range(num_distributions):
            if running_qty <= 0:
                break
                
            # Random date in past 30 days
            days_ago = random.randint(1, 30)
            trans_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Distribute some portion
            max_dist = min(running_qty, 25)
            if max_dist <= 0:
                break
            qty = random.randint(1, int(max_dist))
            
            # Calculate COGS
            avg_cost = int(running_cost / running_qty) if running_qty > 0 else 0
            cogs = qty * avg_cost
            
            # Reason code (80% CLIENT, 10% SPOILAGE, 10% INTERNAL)
            rand = random.random()
            if rand < 0.8:
                reason = "CLIENT"
            elif rand < 0.9:
                reason = "SPOILAGE"
            else:
                reason = "INTERNAL"
            
            cursor.execute("""
                INSERT INTO inventory_transactions 
                (item_id, transaction_type, quantity_change, unit_cost_cents, total_financial_impact_cents, reason_code, transaction_date)
                VALUES (?, 'DISTRIBUTION', ?, ?, ?, ?, ?)
            """, (item_id, -qty, avg_cost, cogs, reason, trans_date))
            
            running_qty -= qty
            running_cost -= cogs
            transaction_count += 1
        
        # Update final item state
        final_cost = max(0, running_cost)
        final_qty = max(0, running_qty)
        cursor.execute("""
            UPDATE inventory_items 
            SET quantity_on_hand = ?, total_cost_basis_cents = ?
            WHERE id = ?
        """, (final_qty, final_cost, item_id))
    
    conn.commit()
    
    print(f"Created {transaction_count} sample transactions")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    cursor.execute("SELECT COUNT(*) as count FROM inventory_items WHERE is_active = 1")
    item_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(quantity_on_hand) as total FROM inventory_items WHERE is_active = 1")
    total_qty = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT SUM(total_cost_basis_cents) as total FROM inventory_items WHERE is_active = 1")
    total_value = (cursor.fetchone()['total'] or 0) / 100
    
    print("\n" + "=" * 50)
    print("DEMO DATA SUMMARY")
    print("=" * 50)
    print(f"Active Items:     {item_count}")
    print(f"Total Quantity:   {total_qty:,.0f} units")
    print(f"Total Value:      ${total_value:,.2f}")
    print(f"Transactions:     {transaction_count}")
    print("=" * 50)
    print("\nDemo data populated successfully!")


def main():
    """Main entry point."""
    # Default to AppData location
    appdata_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 
        'AIOpsStudio'
    )
    db_path = os.path.join(appdata_dir, 'inventory.db')
    
    # Allow override via command line
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        print("Please run the application first to create the database.")
        sys.exit(1)
    
    # Confirm before overwriting
    print(f"This will populate demo data in: {db_path}")
    print("WARNING: This may affect existing data!")
    response = input("Continue? (y/N): ").strip().lower()
    
    if response != 'y':
        print("Aborted.")
        sys.exit(0)
    
    populate_demo_data(db_path)


if __name__ == "__main__":
    main()
