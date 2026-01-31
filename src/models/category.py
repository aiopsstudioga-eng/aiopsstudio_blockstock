"""
Category model for AIOps Studio - Inventory.

Represents hierarchical categorization of inventory items.
"""

from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    """Represents an item category with optional parent-child hierarchy."""
    
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        """String representation of category."""
        return self.name
    
    @classmethod
    def from_db_row(cls, row) -> 'Category':
        """
        Create Category instance from database row.
        
        Args:
            row: SQLite row object
            
        Returns:
            Category: Category instance
        """
        return cls(
            id=row['id'],
            name=row['name'],
            parent_id=row['parent_id'],
            description=row['description'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
    
    def to_dict(self) -> dict:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
