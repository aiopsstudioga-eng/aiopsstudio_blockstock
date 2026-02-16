import sys
import os
import sqlite3
import shutil
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from main import setup_database

def test_db_repair():
    print("Testing Database Repair Logic...")
    
    test_dir = Path("db_repair_test")
    test_dir.mkdir(exist_ok=True)
    
    db_name = "test_inventory.db"
    db_path = test_dir / db_name
    
    # 1. Test Case: Database file exists but is empty (simulating the bug)
    print("\n--- Test Case 1: Empty File ---")
    with open(db_path, 'w') as f:
        pass # Create empty file
        
    print(f"Created empty file at {db_path}, size: {os.path.getsize(db_path)} bytes")
    
    # Run setup
    try:
        setup_database(str(test_dir), db_name)
    except SystemExit:
        print("FAIL: setup_database called sys.exit()")
        return

    # Verify tables exist
    if verify_tables(db_path):
        print("PASS: Database initialized despite existing empty file.")
    else:
        print("FAIL: Database tables not created.")

    # 2. Test Case: Database file exists and has tables (Idempotency)
    print("\n--- Test Case 2: Existing Valid Database ---")
    # It should already be valid from step 1. Run again.
    try:
        setup_database(str(test_dir), db_name)
    except SystemExit:
        print("FAIL: setup_database called sys.exit()")
        return
        
    if verify_tables(db_path):
        print("PASS: Existing database preserved/verified.")
    else:
        print("FAIL: Database corrupted or check failed.")

def verify_tables(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_items'")
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    try:
        test_db_repair()
    finally:
        # Cleanup
        if os.path.exists("db_repair_test"):
            try:
                shutil.rmtree("db_repair_test")
                print("\nCleanup successful.")
            except Exception as e:
                print(f"Cleanup failed: {e}")
