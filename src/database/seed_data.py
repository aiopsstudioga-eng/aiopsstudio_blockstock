import sqlite3
import os
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

def seed_training_data(target_db_path):
    """
    Seed the training database by cloning items from production inventory.db
    and creating dummy transactions to match current stock.
    """
    # Assume inventory.db is in the same directory as training.db (target_db_path)
    base_dir = os.path.dirname(target_db_path)
    source_db_path = os.path.join(base_dir, "inventory.db")
    
    logger.info(f"Seeding training data from {source_db_path} to {target_db_path}...")
    
    if not os.path.exists(source_db_path):
        logger.warning(f"Source database {source_db_path} not found. Cannot seed from production.")
        return

    # Connect to Training DB (Target)
    conn_target = sqlite3.connect(target_db_path)
    cursor_target = conn_target.cursor()
    
    # Connect to Production DB (Source) - Open read-only if possible or just standard
    try:
        conn_source = sqlite3.connect(f"file:{source_db_path}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        # Fallback if URI not supported or other issue
        conn_source = sqlite3.connect(source_db_path)
        
    cursor_source = conn_source.cursor()
    
    try:
        # 1. Copy Categories (to ensure FKs valid, though schema has defaults)
        # Actually schema.sql already inserts default categories. 
        # But user might have added custom ones.
        logger.info("Copying categories...")
        cursor_source.execute("SELECT * FROM item_categories")
        categories = cursor_source.fetchall()
        
        # Clear default categories to avoid conflicts or use INSERT OR REPLACE
        cursor_target.executemany("""
            INSERT OR REPLACE INTO item_categories (id, name, parent_id, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, categories)
        
        # 2. Copy Items
        logger.info("Copying items...")
        cursor_source.execute("SELECT * FROM inventory_items")
        items = cursor_source.fetchall()
        
        # Get column names to map correctly if needed, but assuming schema match
        # schema for items: id, sku, name, category_id, quantity_on_hand, reorder_threshold, 
        # total_cost_basis_cents, is_active, created_at, updated_at
        
        if not items:
            logger.info("No items found in production database.")
        
        cursor_target.executemany("""
            INSERT OR REPLACE INTO inventory_items 
            (id, sku, name, category_id, quantity_on_hand, reorder_threshold, 
             total_cost_basis_cents, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, items)
        
        # 3. Generate Transactions
        # For each item with quantity > 0, we need a transaction so it can be Voided.
        logger.info("Generating initial history for training...")
        
        now = datetime.now()
        
        for item in items:
            # item structure matches SELECT * order. 
            # id=0, sku=1, name=2... quantity_on_hand=4, total_cost_basis=6
            item_id = item[0]
            qty = item[4]
            cost_basis = item[6]
            
            if qty > 0:
                # Create a "Purchase" representing the starting balance
                # Unit cost = Basis / Qty
                unit_cost = int(cost_basis / qty) if qty else 0
                
                cursor_target.execute("""
                    INSERT INTO inventory_transactions
                    (item_id, transaction_type, quantity_change, unit_cost_cents, 
                     total_financial_impact_cents, transaction_date, notes, supplier, created_by)
                    VALUES (?, 'PURCHASE', ?, ?, 0, ?, 'Training Mode Opening Balance', 'System Seed', 'system')
                """, (item_id, qty, unit_cost, now))
                
        conn_target.commit()
        logger.info("Seeding complete.")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}", exc_info=True)
        conn_target.rollback()
    finally:
        conn_source.close()
        conn_target.close()
