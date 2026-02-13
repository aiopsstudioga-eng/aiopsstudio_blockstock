import sqlite3
import os

def get_app_data_db_path(filename="inventory.db"):
    """Get the path to the AppData database file."""
    app_data = os.getenv('LOCALAPPDATA')
    if not app_data:
        app_data = os.path.expanduser('~\\AppData\\Local')
    
    app_dir = os.path.join(app_data, 'AIOpsStudio')
    return os.path.join(app_dir, filename)

def fix_check_constraints(db_filename):
    """
    Recreate inventory_transactions table with updated CHECK constraints
    to allow CORRECTION transaction type.
    """
    db_path = get_app_data_db_path(db_filename)
    print(f"Fixing constraints for: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Skipping.")
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF") # Important for table recreation
    cursor = conn.cursor()
    
    try:
        conn.execute("BEGIN TRANSACTION")
        
        # 1. Rename existing table
        print("Renaming old table...")
        cursor.execute("ALTER TABLE inventory_transactions RENAME TO inventory_transactions_old")
        
        # 2. Create new table with updated CHECK constraints
        print("Creating new table...")
        cursor.execute("""
            CREATE TABLE inventory_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity_change REAL NOT NULL,
                unit_cost_cents INTEGER DEFAULT 0,
                fair_market_value_cents INTEGER DEFAULT 0,
                total_financial_impact_cents INTEGER DEFAULT 0,
                reason_code TEXT,
                supplier TEXT,
                donor TEXT,
                notes TEXT,
                transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                is_voided BOOLEAN DEFAULT 0,
                ref_transaction_id INTEGER,
                FOREIGN KEY (item_id) REFERENCES inventory_items(id),
                FOREIGN KEY (ref_transaction_id) REFERENCES inventory_transactions(id),
                CHECK (transaction_type IN ('PURCHASE', 'DONATION', 'DISTRIBUTION', 'CORRECTION')),
                CHECK (
                    (transaction_type = 'DISTRIBUTION' AND quantity_change < 0) OR
                    (transaction_type IN ('PURCHASE', 'DONATION') AND quantity_change > 0) OR
                    (transaction_type = 'CORRECTION')
                )
            )
        """)
        
        # 3. Copy data from old table
        print("Copying data...")
        # Get columns from old table to ensure match
        cursor.execute("PRAGMA table_info(inventory_transactions_old)")
        columns = [row[1] for row in cursor.fetchall()]
        col_str = ", ".join(columns)
        
        cursor.execute(f"INSERT INTO inventory_transactions ({col_str}) SELECT {col_str} FROM inventory_transactions_old")
        
        # 4. Drop old table
        print("Dropping old table...")
        cursor.execute("DROP TABLE inventory_transactions_old")
        
        # 5. Recreate Indexes
        print("Recreating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_item ON inventory_transactions(item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_date ON inventory_transactions(transaction_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_type ON inventory_transactions(transaction_type)")
        
        conn.commit()
        print(f"Constraints fixed for {db_filename}.")
        
    except Exception as e:
        print(f"Error fixing constraints: {e}")
        conn.rollback()
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

if __name__ == "__main__":
    fix_check_constraints("inventory.db")
    fix_check_constraints("training.db")
