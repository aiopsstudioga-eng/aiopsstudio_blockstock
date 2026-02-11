"""
Unit tests for weighted average cost calculations.

These tests validate the core accounting logic of the inventory system.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from models.item import InventoryItem


class TestWeightedAverageCost:
    """Test weighted average cost calculations."""
    
    def test_initial_unit_cost_is_zero(self):
        """Test that new items have zero unit cost."""
        item = InventoryItem(sku="TEST001", name="Test Item")
        assert item.current_unit_cost_cents == 0
        assert item.current_unit_cost_dollars == 0.0
    
    def test_purchase_updates_weighted_average(self):
        """Test that purchases correctly update weighted average cost."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=100,
            total_cost_basis_cents=20000  # $200 total, $2.00 per unit
        )
        
        # Current state: 100 units @ $2.00/unit = $200 total
        assert item.current_unit_cost_cents == 200  # $2.00
        
        # Purchase 50 units @ $3.00/unit = $150 total
        incoming_qty = 50
        incoming_cost_cents = 15000  # $150 total
        
        new_qty, new_basis = item.calculate_purchase_state(incoming_qty, incoming_cost_cents)
        
        # Update item state to verify unit cost property
        item.quantity_on_hand = new_qty
        item.total_cost_basis_cents = new_basis
        
        # Expected: ($200 + $150) / (100 + 50) = $350 / 150 = $2.333... = 233 cents
        assert item.current_unit_cost_cents == 233
    
    def test_donation_does_not_affect_cost_basis(self):
        """Test that donations (zero cost) reduce the weighted average."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=100,
            total_cost_basis_cents=20000  # $200 total, $2.00 per unit
        )
        
        # Current state: 100 units @ $2.00/unit
        assert item.current_unit_cost_cents == 200
        
        # Donate 50 units @ $0.00/unit (zero cost)
        incoming_qty = 50
        incoming_cost_cents = 0  # Donation has no cost
        
        new_qty, new_basis = item.calculate_purchase_state(incoming_qty, incoming_cost_cents)
        
        # Update item state
        item.quantity_on_hand = new_qty
        item.total_cost_basis_cents = new_basis
        
        # Expected: ($200 + $0) / (100 + 50) = $200 / 150 = $1.33/unit = 133 cents
        assert item.current_unit_cost_cents == 133
        
        # Cost basis should not change
        assert new_basis == 20000
    
    def test_integer_arithmetic_prevents_floating_point_errors(self):
        """Test that using cents prevents floating-point precision errors."""
        # This is the classic floating-point problem
        # 10.10 + 0.20 = 10.299999999999999 (in floating point)
        
        # Using cents (integers)
        cost1_cents = 1010  # $10.10
        cost2_cents = 20    # $0.20
        total_cents = cost1_cents + cost2_cents
        
        assert total_cents == 1030  # Exactly $10.30
        assert total_cents / 100 == 10.30  # Perfect conversion to dollars
    
    def test_complex_scenario_multiple_transactions(self):
        """Test weighted average with multiple purchases and donations."""
        item = InventoryItem(sku="TEST001", name="Test Item")
        
        # Transaction 1: Purchase 100 units @ $1.00/unit
        item.quantity_on_hand = 100
        item.total_cost_basis_cents = 10000
        assert item.current_unit_cost_cents == 100  # $1.00
        
        # Transaction 2: Donate 50 units @ $0.00/unit
        new_qty, new_basis = item.calculate_purchase_state(50, 0)
        item.quantity_on_hand = new_qty
        item.total_cost_basis_cents = new_basis
        
        assert item.quantity_on_hand == 150
        assert item.total_cost_basis_cents == 10000  # Unchanged
        assert item.current_unit_cost_cents == 66  # $0.66 (rounded down)
        
        # Transaction 3: Purchase 50 units @ $2.00/unit
        new_qty, new_basis = item.calculate_purchase_state(50, 10000)
        item.quantity_on_hand = new_qty
        item.total_cost_basis_cents = new_basis
        
        assert item.quantity_on_hand == 200
        assert item.total_cost_basis_cents == 20000
        assert item.current_unit_cost_cents == 100  # $1.00
        
        # Transaction 4: Distribute 100 units (COGS = 100 * $1.00 = $100)
        # Use calculate_distribution_state
        new_qty, new_basis, cogs_cents = item.calculate_distribution_state(100)
        
        assert cogs_cents == 10000  # $100 COGS
        assert new_qty == 100
        assert new_basis == 10000
    
    def test_zero_quantity_returns_zero_cost(self):
        """Test that zero inventory returns zero unit cost."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=0,
            total_cost_basis_cents=0
        )
        
        assert item.current_unit_cost_cents == 0
    
    def test_validation_prevents_negative_quantity(self):
        """Test that negative quantities are rejected."""
        with pytest.raises(ValueError, match="cannot be negative"):
            item = InventoryItem(
                sku="TEST001",
                name="Test Item",
                quantity_on_hand=-10
            )
    
    def test_validation_prevents_negative_cost_basis(self):
        """Test that negative cost basis is rejected."""
        with pytest.raises(ValueError, match="cannot be negative"):
            item = InventoryItem(
                sku="TEST001",
                name="Test Item",
                total_cost_basis_cents=-100
            )
    
    def test_can_distribute_validation(self):
        """Test distribution quantity validation."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=100
        )
        
        assert item.can_distribute(50) is True
        assert item.can_distribute(100) is True
        assert item.can_distribute(101) is False
    
    def test_below_threshold_detection(self):
        """Test reorder threshold detection."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=5,
            reorder_threshold=10
        )
        
        assert item.is_below_threshold() is True
        
        item.quantity_on_hand = 15
        assert item.is_below_threshold() is False
    
    def test_dollar_cent_conversion_properties(self):
        """Test dollar/cent conversion properties."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=100,
            total_cost_basis_cents=25050  # $250.50
        )
        
        assert item.total_cost_basis_dollars == 250.50
        assert item.current_unit_cost_cents == 250  # $2.50 per unit (rounded down)
        assert item.current_unit_cost_dollars == 2.50
        assert item.total_inventory_value_dollars == 250.50


class TestInventoryItemModel:
    """Test InventoryItem model functionality."""
    
    def test_item_creation(self):
        """Test creating an inventory item."""
        item = InventoryItem(
            sku="BEAN001",
            name="Canned Beans",
            category_id=3,
            quantity_on_hand=50,
            reorder_threshold=20,
            total_cost_basis_cents=5000
        )
        
        assert item.sku == "BEAN001"
        assert item.name == "Canned Beans"
        assert item.category_id == 3
        assert item.quantity_on_hand == 50
        assert item.reorder_threshold == 20
        assert item.total_cost_basis_cents == 5000
        assert item.is_active is True
    
    def test_item_to_dict(self):
        """Test converting item to dictionary."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=100,
            total_cost_basis_cents=10000
        )
        
        data = item.to_dict()
        
        assert data['sku'] == "TEST001"
        assert data['name'] == "Test Item"
        assert data['quantity_on_hand'] == 100
        assert data['total_cost_basis_cents'] == 10000
        assert data['current_unit_cost_cents'] == 100
        assert data['current_unit_cost_dollars'] == 1.00
        assert 'is_below_threshold' in data
    
    def test_item_string_representation(self):
        """Test item string representation."""
        item = InventoryItem(
            sku="TEST001",
            name="Test Item",
            quantity_on_hand=50
        )
        
        assert str(item) == "Test Item (TEST001) - 50"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
