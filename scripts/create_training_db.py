"""
Create training database from production inventory.

Copies all items from inventory.db to training.db and populates with demo transactions.
This allows users to practice without affecting real inventory data.

Usage:
    python scripts/create_training_db.py
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
import random

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import DatabaseManager


def create_training_database():
    """Create training.db from inventory.db with demo transactions."""
    
    # Get AppData path
    appdata_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 
        'AIOpsStudio'
    )
    
    inventory_db = os.path.join(appdata_dir, 'inventory.db')
    training_db = os.path.join(appdata_dir, 'training.db')
    
    # Check if inventory.db exists
    if not os.path.exists(inventory_db):
        print(f"ERROR: Production database not found at {inventory_db}")
        print("Please run the application first to create the database.")
        sys.exit(1)
    
    print(f"Source (Production): {inventory_db}")
    print(f"Target (Training):   {training_db}")
    
    # Backup or remove existing training.db
    if os.path.exists(training_db):
        print("\nExisting training.db found.")
        response = input("Replace it? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)
        os.remove(training_db)
        # Also remove WAL files if present
        for ext in ['-wal', '-shm']:
            wal_file = training_db + ext
            if os.path.exists(wal_file):
                os.remove(wal_file)
    
    # Copy inventory.db to training.db
    print("\nCopying inventory structure and items to training.db...")
    shutil.copy2(inventory_db, training_db)
    
    # Connect to training database
    db_manager = DatabaseManager(training_db)
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Clear any existing transactions (start fresh for training)
    print("Clearing existing transactions...")
    cursor.execute("DELETE FROM inventory_transactions")
    conn.commit()
    
    # Reset all item quantities and cost basis to zero
    print("Resetting item quantities...")
    cursor.execute("UPDATE inventory_items SET quantity_on_hand = 0, total_cost_basis_cents = 0")
    conn.commit()
    
    # Get all active items
    cursor.execute("SELECT id, name, sku FROM inventory_items WHERE is_active = 1")
    items = cursor.fetchall()
    
    print(f"\nPopulating demo data for {len(items)} items...")
    
    # Suppliers and Donors
    suppliers = ["ACME Foods", "Sysco", "US Foods", "Local Grocery Co", "Costco Business"]
    donors = ["First Baptist Church", "Community Foundation", "Food Drive 2026", "Anonymous", "Local Business Guild"]
    
    transaction_count = 0
    
    for item in items:
        item_id = item['id']
        item_name = item['name']
        
        running_qty = 0
        running_cost = 0
        
        # Generate 2-4 intake transactions per item
        num_intakes = random.randint(2, 4)
        
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
    
    # Summary
    cursor.execute("SELECT COUNT(*) as count FROM inventory_items WHERE is_active = 1")
    item_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(quantity_on_hand) as total FROM inventory_items WHERE is_active = 1")
    total_qty = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT SUM(total_cost_basis_cents) as total FROM inventory_items WHERE is_active = 1")
    total_value = (cursor.fetchone()['total'] or 0) / 100
    
    print("\n" + "=" * 50)
    print("TRAINING DATABASE CREATED")
    print("=" * 50)
    print(f"Location:         {training_db}")
    print(f"Active Items:     {item_count}")
    print(f"Total Quantity:   {total_qty:,.0f} units")
    print(f"Total Value:      ${total_value:,.2f}")
    print(f"Transactions:     {transaction_count}")
    print("=" * 50)
    print("\n✅ Training database ready!")
    print("Start the app and select 'Training Mode' to use it.")


if __name__ == "__main__":
    create_training_database()
