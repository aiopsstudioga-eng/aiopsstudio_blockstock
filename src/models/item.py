"""
InventoryItem model for AIOps Studio - Inventory.

Represents an inventory item with weighted average cost tracking.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class InventoryItem:
    """
    Represents an inventory item with weighted average cost accounting.
    
    The core of the inventory system - tracks current state and calculates
    weighted average cost for accurate COGS reporting.
    """
    
    sku: str
    name: str
    category_id: Optional[int] = None
    # uom removed
    quantity_on_hand: float = 0.0
    reorder_threshold: int = 10
    total_cost_basis_cents: int = 0  # Total actual money invested
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validate item data after initialization."""
        if self.quantity_on_hand < 0:
            raise ValueError("Quantity on hand cannot be negative")
        if self.total_cost_basis_cents < 0:
            raise ValueError("Total cost basis cannot be negative")
    
    @property
    def current_unit_cost_cents(self) -> int:
        """
        Calculate current weighted average unit cost in cents.

        Uses round() instead of int() to avoid systematic truncation that would
        cause cumulative cost-basis drift over many transactions.

        Returns:
            int: Current unit cost in cents (0 if no inventory)
        """
        if self.quantity_on_hand <= 0:
            return 0
        return round(self.total_cost_basis_cents / self.quantity_on_hand)
    
    @property
    def current_unit_cost_dollars(self) -> float:
        """Get current unit cost in dollars."""
        return self.current_unit_cost_cents / 100.0
    
    @property
    def total_cost_basis_dollars(self) -> float:
        """Get total cost basis in dollars."""
        return self.total_cost_basis_cents / 100.0
    
    @property
    def total_inventory_value_cents(self) -> int:
        """
        Calculate total inventory value (quantity * unit cost).
        
        Returns:
            int: Total value in cents
        """
        return self.total_cost_basis_cents
    
    @property
    def total_inventory_value_dollars(self) -> float:
        """Get total inventory value in dollars."""
        return self.total_inventory_value_cents / 100.0
    
    def is_below_threshold(self) -> bool:
        """
        Check if item is below reorder threshold.
        
        Returns:
            bool: True if below threshold
        """
        return self.quantity_on_hand < self.reorder_threshold
    
    def can_distribute(self, quantity: float) -> bool:
        """
        Check if we can distribute the requested quantity.
        
        Args:
            quantity: Quantity to distribute
            
        Returns:
            bool: True if we have enough inventory
        """
        return self.quantity_on_hand >= quantity
    
    def calculate_purchase_state(
        self, 
        quantity: float, 
        total_cost_cents: int
    ) -> tuple[float, int]:
        """
        Calculate new state after a purchase.
        
        Args:
            quantity: Quantity purchased
            total_cost_cents: Total cost of purchase in cents
            
        Returns:
            tuple[float, int]: (new_quantity, new_total_cost_basis_cents)
        """
        if quantity <= 0:
            raise ValueError("Purchase quantity must be positive")
        if total_cost_cents < 0:
            raise ValueError("Purchase cost cannot be negative")
            
        new_quantity = self.quantity_on_hand + quantity
        new_cost_basis = self.total_cost_basis_cents + total_cost_cents
        
        return new_quantity, new_cost_basis

    def calculate_distribution_state(
        self, 
        quantity: float
    ) -> tuple[float, int, int]:
        """
        Calculate new state after a distribution.
        
        Args:
            quantity: Quantity to distribute
            
        Returns:
            tuple[float, int, int]: (new_quantity, new_total_cost_basis_cents, cogs_cents)
            
        Raises:
            ValueError: If insufficient inventory
        """
        if quantity <= 0:
            raise ValueError("Distribution quantity must be positive")
        if not self.can_distribute(quantity):
            raise ValueError(
                f"Insufficient inventory. Available: {self.quantity_on_hand}, "
                f"Requested: {quantity}"
            )
            
        # Calculate COGS at current weighted average cost.
        # Use round() to avoid systematic truncation causing cost-basis drift.
        unit_cost_cents = self.current_unit_cost_cents
        cogs_cents = round(quantity * unit_cost_cents)
        
        # Calculate new totals
        new_quantity = self.quantity_on_hand - quantity
        new_cost_basis = self.total_cost_basis_cents - cogs_cents
        
        # Ensure cost basis doesn't go negative due to rounding
        if new_cost_basis < 0:
            new_cost_basis = 0
            
        return new_quantity, new_cost_basis, cogs_cents
    
    @classmethod
    def from_db_row(cls, row) -> 'InventoryItem':
        """
        Create InventoryItem instance from database row.
        
        Args:
            row: SQLite row object
            
        Returns:
            InventoryItem: Item instance
        """
        return cls(
            id=row['id'],
            sku=row['sku'],
            name=row['name'],
            category_id=row['category_id'],
            # uom removed
            quantity_on_hand=row['quantity_on_hand'],
            reorder_threshold=row['reorder_threshold'],
            total_cost_basis_cents=row['total_cost_basis_cents'],
            is_active=bool(row['is_active']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )
    
    def to_dict(self) -> dict:
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category_id': self.category_id,
            # 'uom': self.uom, # removed
            'quantity_on_hand': self.quantity_on_hand,
            'reorder_threshold': self.reorder_threshold,
            'total_cost_basis_cents': self.total_cost_basis_cents,
            'current_unit_cost_cents': self.current_unit_cost_cents,
            'current_unit_cost_dollars': self.current_unit_cost_dollars,
            'total_inventory_value_dollars': self.total_inventory_value_dollars,
            'is_active': self.is_active,
            'is_below_threshold': self.is_below_threshold(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self) -> str:
        """String representation of item."""
        return f"{self.name} ({self.sku}) - {self.quantity_on_hand}"
