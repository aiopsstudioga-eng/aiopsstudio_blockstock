#!/usr/bin/env python3
"""
Script to delete ALL data from the inventory database.
WARNING: This is destructive and irreversible.
"""

import sqlite3
import os
import sys

# Assume running from project root
DB_PATH = "inventory.db"

def clear_all_data():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file '{DB_PATH}' not found.")
        print("   Make sure you are running this script from the project root.")
        return

    print(f"⚠️  WARNING: This will delete ALL data from '{DB_PATH}'.")
    # For now, since user asked to "execute" it, we won't add an interactive prompt 
    # that blocks execution, but normally we would.
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable FKs to ensure we don't break integrity (or we just delete in right order)
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    tables_ordered = [
        "inventory_transactions", # Depends on items
        "inventory_items",        # Depends on categories
        "item_categories"         # Base
    ]
    
    try:
        print("Performing deletion...")
        for table in tables_ordered:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✓ Cleared table: {table}")
            
        # Reset autoincrement sequences
        cursor.execute("DELETE FROM sqlite_sequence")
        print("  ✓ Reset IDs (sqlite_sequence)")
        
        conn.commit()
        print("✅ All data cleared successfully.")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_all_data()
