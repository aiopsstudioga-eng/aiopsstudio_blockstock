"""
Inventory Service for AIOps Studio - Inventory.

Business logic layer for inventory operations including:
- Purchase processing (updates weighted average cost)
- Donation processing (zero-cost intake)
- Distribution processing (COGS calculation)
- Item CRUD operations
"""

from typing import List, Optional, Tuple
from datetime import datetime

from models.item import InventoryItem
from models.transaction import Transaction, TransactionType, ReasonCode
from models.category import Category
from database.connection import get_db_manager


class InventoryService:
    """Service layer for inventory operations."""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        Initialize inventory service.
        
        Args:
            db_path: Path to the database file
        """
        self.db_manager = get_db_manager(db_path)
    
    # ========================================================================
    # ITEM CRUD OPERATIONS
    # ========================================================================
    
    def create_item(
        self,
        sku: str,
        name: str,
        category_id: Optional[int] = None,
        reorder_threshold: int = 10
    ) -> InventoryItem:
        """
        Create a new inventory item.
        
        Args:
            sku: Unique SKU identifier
            name: Item name
            category_id: Category ID (optional)
            reorder_threshold: Reorder threshold quantity
            
        Returns:
            InventoryItem: Created item
            
        Raises:
            ValueError: If SKU already exists
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Check if SKU already exists
            cursor.execute("SELECT id FROM inventory_items WHERE sku = ?", (sku,))
            if cursor.fetchone():
                raise ValueError(f"Item with SKU '{sku}' already exists")
            
            # Insert item
            cursor.execute("""
                INSERT INTO inventory_items 
                (sku, name, category_id, reorder_threshold)
                VALUES (?, ?, ?, ?)
            """, (sku, name, category_id, reorder_threshold))
            
            item_id = cursor.lastrowid
            
            # Fetch and return created item
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            
        return InventoryItem.from_db_row(row)
    
    def get_item(self, item_id: int) -> Optional[InventoryItem]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            InventoryItem or None if not found
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        
        if row:
            return InventoryItem.from_db_row(row)
        return None
    
    def get_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """
        Get item by SKU.
        
        Args:
            sku: Item SKU
            
        Returns:
            InventoryItem or None if not found
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inventory_items WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        
        if row:
            return InventoryItem.from_db_row(row)
        return None
    
    def get_all_items(self, active_only: bool = True) -> List[InventoryItem]:
        """
        Get all inventory items.
        
        Args:
            active_only: If True, only return active items
            
        Returns:
            List of InventoryItem
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("SELECT * FROM inventory_items WHERE is_active = 1 ORDER BY name")
        else:
            cursor.execute("SELECT * FROM inventory_items ORDER BY name")
        
        return [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
    
    def search_items_by_prefix(self, prefix: str, limit: int = 15) -> List[InventoryItem]:
        """
        Search active items by SKU or name prefix for autocomplete.
        
        Uses LIKE query which leverages the idx_items_sku index for SKU matches.
        
        Args:
            prefix: The prefix to search for (minimum 2 chars recommended)
            limit: Maximum results to return
            
        Returns:
            List of matching InventoryItem, ordered by SKU
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        pattern = f"{prefix}%"
        cursor.execute("""
            SELECT * FROM inventory_items 
            WHERE is_active = 1 
              AND (sku LIKE ? OR name LIKE ?)
            ORDER BY sku
            LIMIT ?
        """, (pattern, pattern, limit))
        
        return [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
    
    def update_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        reorder_threshold: Optional[int] = None
    ) -> InventoryItem:
        """
        Update item properties.
        
        Args:
            item_id: Item ID
            name: New name (optional)
            category_id: New category ID (optional)
            reorder_threshold: New reorder threshold (optional)
            
        Returns:
            InventoryItem: Updated item
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if category_id is not None:
                updates.append("category_id = ?")
                params.append(category_id)
            
            if reorder_threshold is not None:
                updates.append("reorder_threshold = ?")
                params.append(reorder_threshold)
            
            if not updates:
                raise ValueError("No updates provided")
            
            params.append(item_id)
            
            cursor.execute(f"""
                UPDATE inventory_items 
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            # Fetch and return updated item
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            
        return InventoryItem.from_db_row(row)
    
    def soft_delete_item(self, item_id: int) -> InventoryItem:
        """
        Soft delete an item (set is_active = False).
        
        Args:
            item_id: Item ID
            
        Returns:
            InventoryItem: Deleted item
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE inventory_items 
                SET is_active = 0
                WHERE id = ?
            """, (item_id,))
            
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            
        return InventoryItem.from_db_row(row)
    
    def get_items_below_threshold(self) -> List[InventoryItem]:
        """
        Get all items below their reorder threshold.
        
        Returns:
            List of InventoryItem below threshold
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inventory_items 
            WHERE is_active = 1 
            AND quantity_on_hand < reorder_threshold
            ORDER BY name
        """)
        
        return [InventoryItem.from_db_row(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # TRANSACTION PROCESSING - THE CORE BUSINESS LOGIC
    # ========================================================================
    
    def process_purchase(
        self,
        item_id: int,
        quantity: float,
        unit_cost_dollars: float,
        supplier: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[InventoryItem, Transaction]:
        """
        Process a purchase transaction.
        
        Updates inventory quantity and weighted average cost.
        
        Args:
            item_id: Item ID
            quantity: Quantity purchased
            unit_cost_dollars: Cost per unit in dollars
            supplier: Supplier name (optional)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (updated InventoryItem, Transaction)
            
        Raises:
            ValueError: If item not found or invalid quantity/cost
        """
        if quantity <= 0:
            raise ValueError("Purchase quantity must be positive")
        if unit_cost_dollars < 0:
            raise ValueError("Unit cost cannot be negative")
        
        # Convert dollars to cents
        unit_cost_cents = int(unit_cost_dollars * 100)
        total_cost_cents = int(quantity * unit_cost_cents)
        
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Get current item state
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Item with ID {item_id} not found")
            
            item = InventoryItem.from_db_row(row)
            
            # Calculate new totals using Model logic
            new_quantity, new_cost_basis = item.calculate_purchase_state(
                quantity, total_cost_cents
            )
            
            # Update item
            cursor.execute("""
                UPDATE inventory_items
                SET quantity_on_hand = ?,
                    total_cost_basis_cents = ?
                WHERE id = ?
            """, (new_quantity, new_cost_basis, item_id))
            
            # Create transaction record
            cursor.execute("""
                INSERT INTO inventory_transactions
                (item_id, transaction_type, quantity_change, unit_cost_cents, 
                 supplier, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (item_id, TransactionType.PURCHASE.value, quantity, 
                  unit_cost_cents, supplier, notes))
            
            transaction_id = cursor.lastrowid
            
            # Fetch updated item and transaction
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            updated_item = InventoryItem.from_db_row(cursor.fetchone())
            
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", 
                         (transaction_id,))
            transaction = Transaction.from_db_row(cursor.fetchone())
        
        return updated_item, transaction
    
    def process_donation(
        self,
        item_id: int,
        quantity: float,
        fair_market_value_dollars: float = 0.0,
        donor: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[InventoryItem, Transaction]:
        """
        Process a donation transaction.
        
        Increases inventory but does NOT affect cost basis (cost = $0).
        Fair market value is tracked separately for impact reporting.
        
        Args:
            item_id: Item ID
            quantity: Quantity donated
            fair_market_value_dollars: Estimated market value per unit
            donor: Donor name (optional)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (updated InventoryItem, Transaction)
        """
        if quantity <= 0:
            raise ValueError("Donation quantity must be positive")
        
        # Convert dollars to cents
        fmv_cents = int(fair_market_value_dollars * 100)
        total_fmv_cents = int(quantity * fmv_cents)
        
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Get current item state
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Item with ID {item_id} not found")
            
            item = InventoryItem.from_db_row(row)
            
            # Calculate new quantity (cost basis unchanged for donations)
            new_quantity = item.quantity_on_hand + quantity
            
            # Update item
            cursor.execute("""
                UPDATE inventory_items
                SET quantity_on_hand = ?
                WHERE id = ?
            """, (new_quantity, item_id))
            
            # Create transaction record (unit_cost_cents = 0 for donations)
            cursor.execute("""
                INSERT INTO inventory_transactions
                (item_id, transaction_type, quantity_change, unit_cost_cents,
                 fair_market_value_cents, donor, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_id, TransactionType.DONATION.value, quantity, 
                  0, total_fmv_cents, donor, notes))
            
            transaction_id = cursor.lastrowid
            
            # Fetch updated item and transaction
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            updated_item = InventoryItem.from_db_row(cursor.fetchone())
            
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", 
                         (transaction_id,))
            transaction = Transaction.from_db_row(cursor.fetchone())
        
        return updated_item, transaction
    
    def process_distribution(
        self,
        item_id: int,
        quantity: float,
        reason_code: str,
        notes: Optional[str] = None
    ) -> Tuple[InventoryItem, Transaction]:
        """
        Process a distribution transaction.
        
        Decreases inventory and calculates COGS at weighted average cost.
        
        Args:
            item_id: Item ID
            quantity: Quantity to distribute
            reason_code: Reason for distribution (CLIENT, SPOILAGE, INTERNAL)
            notes: Additional notes (optional)
            
        Returns:
            Tuple of (updated InventoryItem, Transaction)
            
        Raises:
            ValueError: If insufficient inventory or invalid quantity
        """
        if quantity <= 0:
            raise ValueError("Distribution quantity must be positive")
        
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Get current item state
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Item with ID {item_id} not found")
            
            item = InventoryItem.from_db_row(row)
            
            # Calculate new totals using Model logic
            # This handles validation, COGS calculation, and state updates
            new_quantity, new_cost_basis, total_financial_impact_cents = item.calculate_distribution_state(
                quantity
            )
            
            # Get unit cost for the record (using current state before update is fine as avg doesn't change on distribution)
            unit_cost_cents = item.current_unit_cost_cents
            
            # Update item
            cursor.execute("""
                UPDATE inventory_items
                SET quantity_on_hand = ?,
                    total_cost_basis_cents = ?
                WHERE id = ?
            """, (new_quantity, new_cost_basis, item_id))
            
            # Create transaction record (negative quantity for distribution)
            # Ensure reason_code is a string (handle Enum if passed)
            reason_str = reason_code.value if hasattr(reason_code, 'value') else reason_code
            
            cursor.execute("""
                INSERT INTO inventory_transactions
                (item_id, transaction_type, quantity_change, unit_cost_cents,
                 total_financial_impact_cents, reason_code, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_id, TransactionType.DISTRIBUTION.value, -quantity,
                  unit_cost_cents, total_financial_impact_cents, reason_str, notes))
            
            transaction_id = cursor.lastrowid
            
            # Fetch updated item and transaction
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
            updated_item = InventoryItem.from_db_row(cursor.fetchone())
            
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", 
                         (transaction_id,))
            transaction = Transaction.from_db_row(cursor.fetchone())
        
        return updated_item, transaction
    
    # ========================================================================
    # TRANSACTION HISTORY
    # ========================================================================
    
    def get_item_transactions(
        self,
        item_id: int,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transaction history for an item.
        
        Args:
            item_id: Item ID
            limit: Maximum number of transactions to return (optional)
            
        Returns:
            List of Transaction, most recent first
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM inventory_transactions 
            WHERE item_id = ?
            ORDER BY transaction_date DESC, id DESC
        """

        # P1-4: Use parameterized LIMIT to prevent SQL injection
        params: list = [item_id]
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        
        return [Transaction.from_db_row(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # CATEGORY OPERATIONS
    # ========================================================================
    
    
    def get_all_categories(self) -> List[Category]:
        """
        Get all categories.
        
        Returns:
            List of Category
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM item_categories ORDER BY name")
        
        return [Category.from_db_row(row) for row in cursor.fetchall()]

    # ========================================================================
    # VOID / CORRECTION OPERATIONS
    # ========================================================================

    def void_transaction(
        self,
        transaction_id: int,
        reason: str
    ) -> Tuple[InventoryItem, Transaction, Transaction]:
        """
        Void a transaction by creating a compensating correction transaction.
        
        Args:
            transaction_id: ID of the transaction to void
            reason: Reason for voiding
            
        Returns:
            Tuple of (Updated Item, Original Transaction, Correction Transaction)
            
        Raises:
            ValueError: If transaction not found, already voided, or logic constraints fail.
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # 1. Fetch original transaction
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            original_tx = Transaction.from_db_row(row)
            
            if original_tx.is_voided:
                raise ValueError(f"Transaction {transaction_id} is already voided")
            
            # 2. Fetch current item state
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (original_tx.item_id,))
            item_row = cursor.fetchone()
            if not item_row:
                raise ValueError(f"Item {original_tx.item_id} not found")
            
            item = InventoryItem.from_db_row(item_row)
            
            # 3. Determine Reversal Logic based on Type
            correction_qty = 0.0
            correction_value_cents = 0
            
            if original_tx.transaction_type == TransactionType.PURCHASE:
                # Voiding a PURCHASE means REMOVING stock and REMOVING cost
                # Constraint: Must have enough stock to remove
                if item.quantity_on_hand < original_tx.quantity_change:
                    raise ValueError(
                        f"Cannot void purchase. Insufficient stock. "
                        f"Have: {item.quantity_on_hand}, Need: {original_tx.quantity_change}"
                    )
                
                # Check if this would make cost negative (shouldn't if logic holds, but safety first)
                if item.total_cost_basis_cents < original_tx.total_financial_impact_cents:
                     # Note: for Purchase, 'unit_cost * qty' determines added value.
                     # Transaction model stores unit_cost_cents. 
                     # original_tx.total_financial_impact_cents is usually 0 for purchases in current model?
                     # Let's re-calculate the value added.
                     pass

                # Calculate value to remove: simple exact reversal of input
                # Input was: qty * unit_cost
                value_to_remove = int(original_tx.quantity_change * original_tx.unit_cost_cents)
                
                new_qty = item.quantity_on_hand - original_tx.quantity_change
                new_cost_basis = item.total_cost_basis_cents - value_to_remove
                
                # Setup correction tx params
                correction_qty = -original_tx.quantity_change
                # financial_impact for correction? null for now, just updating basis.
                
            elif original_tx.transaction_type == TransactionType.DONATION:
                 # Voiding a DONATION means REMOVING stock (Value is 0)
                if item.quantity_on_hand < original_tx.quantity_change:
                     raise ValueError(
                        f"Cannot void donation. Insufficient stock. "
                        f"Have: {item.quantity_on_hand}, Need: {original_tx.quantity_change}"
                    )
                
                new_qty = item.quantity_on_hand - original_tx.quantity_change
                new_cost_basis = item.total_cost_basis_cents # Unchanged
                
                correction_qty = -original_tx.quantity_change

            elif original_tx.transaction_type == TransactionType.DISTRIBUTION:
                # Voiding a DISTRIBUTION means ADDING stock and ADDING back value (COGS)
                # This is "Un-distributing"
                
                # We need to know what the COGS impact was.
                # The 'total_financial_impact_cents' field on the original transaction stores this.
                cogs_to_restore = original_tx.total_financial_impact_cents
                qty_to_restore = abs(original_tx.quantity_change) # distribute is negative, so abs it
                
                new_qty = item.quantity_on_hand + qty_to_restore
                new_cost_basis = item.total_cost_basis_cents + cogs_to_restore
                
                correction_qty = qty_to_restore
            else:
                raise ValueError("Cannot void this transaction type")
            
            # 4. Update Item
            if new_cost_basis < 0:
                new_cost_basis = 0 # Safety floor
                
            cursor.execute("""
                UPDATE inventory_items
                SET quantity_on_hand = ?,
                    total_cost_basis_cents = ?
                WHERE id = ?
            """, (new_qty, new_cost_basis, item.id))
            
            # 5. Create Correction Transaction
            cursor.execute("""
                INSERT INTO inventory_transactions
                (item_id, transaction_type, quantity_change, unit_cost_cents,
                 reason_code, notes, ref_transaction_id, created_by, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                TransactionType.CORRECTION.value,
                correction_qty,
                original_tx.unit_cost_cents, # Keep original unit cost for reference
                ReasonCode.VOID.value,
                f"Void of Tx #{transaction_id}: {reason}",
                transaction_id,
                "system", # TODO: Pass actual user
                datetime.now()
            ))
            correction_id = cursor.lastrowid
            
            # 6. Mark Original as Voided
            cursor.execute("""
                UPDATE inventory_transactions
                SET is_voided = 1
                WHERE id = ?
            """, (transaction_id,))
            
            # Fetch return objects
            cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item.id,))
            updated_item = InventoryItem.from_db_row(cursor.fetchone())
            
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", (correction_id,))
            correction_tx = Transaction.from_db_row(cursor.fetchone())
            
            # Refresh original object to show voided state
            cursor.execute("SELECT * FROM inventory_transactions WHERE id = ?", (transaction_id,))
            original_tx_updated = Transaction.from_db_row(cursor.fetchone())
            
            return updated_item, original_tx_updated, correction_tx

    def get_transactions_by_item(self, item_id: int) -> List[Transaction]:
        """
        Get all transactions for a specific item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            List of Transaction objects
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inventory_transactions 
            WHERE item_id = ? 
            ORDER BY transaction_date DESC
        """, (item_id,))
        
        return [Transaction.from_db_row(row) for row in cursor.fetchall()]
