"""
Integration tests for AIOps Studio - Inventory.

Tests full workflows using a temporary in-memory database.
"""

import pytest
from datetime import date
import sqlite3

from services.inventory_service import InventoryService
from services.reporting_service import ReportingService
from models.transaction import TransactionType, ReasonCode


@pytest.fixture
def service():
    """Create inventory service with in-memory database."""
    # Use in-memory DB for tests
    service = InventoryService(db_path=":memory:")
    # Initialize schema
    with open("src/database/schema.sql", "r") as f:
        service.db_manager.get_connection().executescript(f.read())
    return service

@pytest.fixture
def reporting_service(service):
    """Create reporting service sharing the same connection (if possible/needed)."""
    # For :memory: databases, each connection is a separate DB unless shared cache is used.
    # To keep it simple, we'll rely on the service to have populated the DB,
    # but since ReportingService opens its own connection, it won't see :memory: data
    # unless we use a file or shared cache.
    # Strategy: Use a temporary file for integration tests requiring both services.
    return None  # Will handle in specific tests


def test_full_item_lifecycle(tmp_path):
    """Test complete lifecycle: Create -> Purchase -> Donate -> Distribute."""
    
    # Setup temporary DB file for reporting service compatibility
    db_file = tmp_path / "test_inventory.db"
    service = InventoryService(str(db_file))
    
    # Initialize schema
    with open("src/database/schema.sql", "r") as f:
        service.db_manager.get_connection().executescript(f.read())
        
    reporting = ReportingService(str(db_file))
    
    # 1. Create Item
    item = service.create_item(
        sku="TEST001",
        name="Test Item",
        category_id=None,
        reorder_threshold=10
    )
    assert item.quantity_on_hand == 0
    assert item.total_cost_basis_cents == 0
    
    # 2. Purchase (Purchase 10 @ $1.00)
    service.process_purchase(
        item_id=item.id,
        quantity=10,
        unit_cost_dollars=1.00,
        supplier="Vendor A"
    )
    
    item = service.get_item(item.id)
    assert item.quantity_on_hand == 10
    assert item.current_unit_cost_dollars == 1.00
    assert item.total_inventory_value_dollars == 10.00
    
    # 3. Donation (Receive 10 @ $2.00 FMV - should reduce avg cost)
    # 10 existing @ $1.00 + 10 donated @ $0.00 = 20 units @ $0.50 avg cost
    service.process_donation(
        item_id=item.id,
        quantity=10,
        fair_market_value_dollars=2.00,
        donor="Donor A"
    )
    
    item = service.get_item(item.id)
    assert item.quantity_on_hand == 20
    assert item.current_unit_cost_dollars == 0.50  # (10 + 0) / 20
    assert item.total_inventory_value_dollars == 10.00 # Still $10 total investment
    
    # 4. Distribution (Distribute 5 units)
    # Should reduce inventory and record COGS at current avg cost ($0.50)
    service.process_distribution(
        item_id=item.id,
        quantity=5,
        reason_code=ReasonCode.CLIENT,
        notes="Family A"
    )
    
    item = service.get_item(item.id)
    assert item.quantity_on_hand == 15
    assert item.current_unit_cost_dollars == 0.50
    assert item.total_inventory_value_dollars == 7.50  # 15 * 0.50
    
    # 5. Verify Reporting
    fin_data = reporting.get_financial_report_data()
    # Total COGS should be 5 units * $0.50 = $2.50
    assert fin_data['total_cogs_dollars'] == 2.50
    
    stock_data = reporting.get_stock_status_data()
    assert stock_data['total_items'] == 1
    assert stock_data['total_value_dollars'] == 7.50


def test_insufficient_inventory(service):
    """Test preventing distribution of more items than available."""
    item = service.create_item("TEST002", "Test Item 2")
    service.process_purchase(item.id, 5, 1.00)
    
    with pytest.raises(ValueError, match="Insufficient inventory"):
        service.process_distribution(item.id, 10, ReasonCode.CLIENT)


def test_soft_delete(service):
    """Test soft delete functionality."""
    item = service.create_item("TEST003", "Delete Me")
    item_id = item.id
    
    service.soft_delete_item(item_id)
    
    # Should not appear in active items list
    active_items = service.get_all_items()
    assert item_id not in [i.id for i in active_items]
    
    # But should still be retrievable directly (marked inactive)
    item = service.get_item(item_id)
    assert not item.is_active


def test_transaction_history(service):
    """Test transaction history retrieval."""
    item = service.create_item("TEST004", "History Item")
    
    service.process_purchase(item.id, 10, 1.00)
    service.process_distribution(item.id, 2, ReasonCode.CLIENT)
    
    history = service.get_item_transactions(item.id)
    assert len(history) == 2
    assert history[0].transaction_type == TransactionType.DISTRIBUTION # Most recent first
    assert history[1].transaction_type == TransactionType.PURCHASE
