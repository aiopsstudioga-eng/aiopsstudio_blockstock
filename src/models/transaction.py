"""
Transaction model for AIOps Studio - Inventory.

Represents immutable inventory transactions (purchases, donations, distributions).
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Types of inventory transactions."""
    PURCHASE = "PURCHASE"
    DONATION = "DONATION"
    DISTRIBUTION = "DISTRIBUTION"
    CORRECTION = "CORRECTION"  # For void/reversal transactions


class ReasonCode(Enum):
    """Reason codes for distributions and corrections."""
    CLIENT = "CLIENT"
    SPOILAGE = "SPOILAGE"
    INTERNAL = "INTERNAL"
    VOID = "VOID"  # Transaction was voided


@dataclass
class Transaction:
    """
    Represents an inventory transaction.
    
    Transactions are immutable once created - they form an audit trail.
    """
    
    item_id: int
    transaction_type: TransactionType
    quantity_change: float
    unit_cost_cents: int = 0
    fair_market_value_cents: int = 0
    total_financial_impact_cents: int = 0
    reason_code: Optional[str] = None
    supplier: Optional[str] = None
    donor: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None
    created_by: str = "system"
    id: Optional[int] = None
    is_voided: bool = False
    ref_transaction_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        # Convert string to enum if needed
        if isinstance(self.transaction_type, str):
            self.transaction_type = TransactionType(self.transaction_type)
        
        # Validate quantity_change sign matches transaction type
        if self.transaction_type == TransactionType.DISTRIBUTION:
            if self.quantity_change >= 0:
                raise ValueError("Distribution transactions must have negative quantity_change")
        elif self.transaction_type in (TransactionType.PURCHASE, TransactionType.DONATION):
            if self.quantity_change <= 0:
                raise ValueError("Purchase/Donation transactions must have positive quantity_change")
        # CORRECTION can be positive or negative depending on what it reverses
    
    @property
    def unit_cost_dollars(self) -> float:
        """Get unit cost in dollars."""
        return self.unit_cost_cents / 100.0
    
    @property
    def fair_market_value_dollars(self) -> float:
        """Get fair market value in dollars."""
        return self.fair_market_value_cents / 100.0
    
    @property
    def total_financial_impact_dollars(self) -> float:
        """Get total financial impact in dollars."""
        return self.total_financial_impact_cents / 100.0
    
    @classmethod
    def from_db_row(cls, row) -> 'Transaction':
        """Create Transaction instance from database row."""
        # Handle new columns safely (for backwards compatibility if row assumes old schema, 
        # though migration should handle it)
        is_voided = bool(row['is_voided']) if 'is_voided' in row.keys() else False
        ref_id = row['ref_transaction_id'] if 'ref_transaction_id' in row.keys() else None
        
        return cls(
            id=row['id'],
            item_id=row['item_id'],
            transaction_type=TransactionType(row['transaction_type']),
            quantity_change=row['quantity_change'],
            unit_cost_cents=row['unit_cost_cents'],
            fair_market_value_cents=row['fair_market_value_cents'],
            total_financial_impact_cents=row['total_financial_impact_cents'],
            reason_code=row['reason_code'],
            supplier=row['supplier'],
            donor=row['donor'],
            notes=row['notes'],
            transaction_date=datetime.fromisoformat(row['transaction_date']) if row['transaction_date'] else None,
            created_by=row['created_by'],
            is_voided=is_voided,
            ref_transaction_id=ref_id
        )
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'transaction_type': self.transaction_type.value,
            'quantity_change': self.quantity_change,
            'unit_cost_cents': self.unit_cost_cents,
            'fair_market_value_cents': self.fair_market_value_cents,
            'total_financial_impact_cents': self.total_financial_impact_cents,
            'reason_code': self.reason_code,
            'supplier': self.supplier,
            'donor': self.donor,
            'notes': self.notes,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_by': self.created_by,
            'is_voided': self.is_voided,
            'ref_transaction_id': self.ref_transaction_id
        }
