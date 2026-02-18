"""
Pytest configuration and shared fixtures for AIOps Studio - Inventory tests.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def isolated_db():
    """
    Provide a clean in-memory SQLite database for every test.

    This fixture runs automatically for all tests (autouse=True).  It resets
    the global DatabaseManager singleton before and after each test so that
    tests never share state or bleed into one another.

    Usage:
        Tests that need an InventoryService or ReportingService should call
        ``get_db_manager(":memory:")`` at the start, or simply instantiate the
        service — the singleton will already be initialised by this fixture.
    """
    from database.connection import get_db_manager, reset_db_manager

    # Clean slate before the test
    reset_db_manager()

    # Initialise a fresh in-memory database and apply the schema
    schema_path = Path(__file__).parent.parent / "src" / "database" / "schema.sql"
    manager = get_db_manager(":memory:")
    with open(schema_path) as f:
        manager.get_connection().executescript(f.read())

    yield manager

    # Tear down after the test
    reset_db_manager()
