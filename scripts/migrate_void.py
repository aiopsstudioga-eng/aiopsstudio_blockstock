
import sys
import os
from pathlib import Path

# Setup path to import src
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from database.connection import get_db_manager

def get_app_data_db_path():
    """Get the path to the AppData database file."""
    app_data = os.getenv('LOCALAPPDATA')
    if not app_data:
        app_data = os.path.expanduser('~\\AppData\\Local')
    
    app_dir = os.path.join(app_data, 'AIOpsStudio')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        
    return os.path.join(app_dir, 'inventory.db')

def migrate_database():
    db_path = get_app_data_db_path()
    print(f"Migrating database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database not found. Initial schema will handle new columns.")
        return

    manager = get_db_manager(db_path)
    
    with manager.transaction() as conn:
        cursor = conn.cursor()
        
        # Check if column exists
        try:
            cursor.execute("SELECT is_voided FROM inventory_transactions LIMIT 1")
            print("Column 'is_voided' already exists.")
        except:
            print("Adding 'is_voided' column...")
            cursor.execute("ALTER TABLE inventory_transactions ADD COLUMN is_voided BOOLEAN DEFAULT 0")

        try:
            cursor.execute("SELECT ref_transaction_id FROM inventory_transactions LIMIT 1")
            print("Column 'ref_transaction_id' already exists.")
        except:
            print("Adding 'ref_transaction_id' column...")
            cursor.execute("ALTER TABLE inventory_transactions ADD COLUMN ref_transaction_id INTEGER REFERENCES inventory_transactions(id)")
            
    print("Migration complete.")

if __name__ == "__main__":
    migrate_database()
