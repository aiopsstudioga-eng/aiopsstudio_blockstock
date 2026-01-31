#!/usr/bin/env python3
"""
Database initialization script for AIOps Studio - Inventory.

This script initializes the SQLite database with the schema and seed data.
Run this script once before first use of the application.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from database.connection import init_database


def main():
    """Initialize the database."""
    print("=" * 60)
    print("AIOps Studio - Inventory")
    print("Database Initialization Script")
    print("=" * 60)
    print()
    
    # Get database path
    project_root = Path(__file__).parent.parent
    db_path = project_root / "inventory.db"
    schema_path = project_root / "src" / "database" / "schema.sql"
    
    # Check if database already exists
    if db_path.exists():
        print(f"⚠️  Database already exists at: {db_path}")
        response = input("Do you want to recreate it? (yes/no): ").lower()
        if response != 'yes':
            print("❌ Initialization cancelled.")
            return
        else:
            print("🗑️  Removing existing database...")
            db_path.unlink()
    
    print(f"📁 Database path: {db_path}")
    print(f"📄 Schema path: {schema_path}")
    print()
    
    # Initialize database
    print("🔨 Creating database and executing schema...")
    try:
        db_manager = init_database(str(db_path), str(schema_path))
        print("✅ Database schema created successfully!")
        print()
        
        # Display database info
        info = db_manager.get_database_info()
        print("📊 Database Information:")
        print(f"   Size: {info['size_mb']} MB")
        print(f"   Tables: {', '.join(info['tables'])}")
        print()
        print("📋 Table Row Counts:")
        for table, count in info['table_counts'].items():
            print(f"   {table}: {count} rows")
        print()
        
        print("✅ Database initialization complete!")
        print()
        print("Next steps:")
        print("  1. Run the application: python src/main.py")
        print("  2. Create your first inventory item")
        print("  3. Start tracking inventory!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
