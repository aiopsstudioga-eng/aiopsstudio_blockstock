"""
Tests for void/correction workflow in AIOps Studio - Inventory.

Covers:
- Voiding a PURCHASE (removes stock + cost basis)
- Voiding a DONATION (removes stock, cost unchanged)
- Voiding a DISTRIBUTION (restores stock + COGS)
- Double-void guard
- Insufficient-stock guard for voiding a purchase
- Not-found transaction guard
- Correction transaction recorded correctly with ref_transaction_id
"""

import pytest

from services.inventory_service import InventoryService
from models.transaction import TransactionType, ReasonCode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc():
    """Return an InventoryService that uses the isolated_db singleton."""
    return InventoryService()


@pytest.fixture
def item(svc):
    """Create a standard test item for each test."""
    return svc.create_item(sku="VOID001", name="Void Test Item")


# ---------------------------------------------------------------------------
# Voiding a PURCHASE
# ---------------------------------------------------------------------------

class TestVoidPurchase:
    """Voiding a purchase removes the stock and the cost that was added."""

    def test_void_purchase_removes_stock(self, svc, item):
        """Stock drops back to zero after voiding the purchase."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)

        updated_item, _orig, _corr = svc.void_transaction(tx.id, reason="Test void")

        assert updated_item.quantity_on_hand == 0

    def test_void_purchase_removes_cost_basis(self, svc, item):
        """Cost basis returns to zero after voiding the purchase."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)

        updated_item, _orig, _corr = svc.void_transaction(tx.id, reason="Test void")

        assert updated_item.total_cost_basis_cents == 0

    def test_void_purchase_marks_original_voided(self, svc, item):
        """The original transaction row is flagged is_voided=True."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)

        _item, orig_tx, _corr = svc.void_transaction(tx.id, reason="Test void")

        assert orig_tx.is_voided is True

    def test_void_purchase_creates_correction_transaction(self, svc, item):
        """A CORRECTION transaction is created that references the original."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)

        _item, _orig, corr_tx = svc.void_transaction(tx.id, reason="Test void")

        assert corr_tx.transaction_type == TransactionType.CORRECTION
        assert corr_tx.ref_transaction_id == tx.id
        assert corr_tx.reason_code == ReasonCode.VOID.value

    def test_void_purchase_insufficient_stock_raises(self, svc, item):
        """Cannot void a purchase if stock was subsequently distributed."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        # Distribute all the stock so voiding the purchase is impossible
        svc.process_distribution(item.id, quantity=10, reason_code=ReasonCode.CLIENT)

        with pytest.raises(ValueError, match="Insufficient stock"):
            svc.void_transaction(tx.id, reason="Cannot void")

    def test_void_purchase_partial_remaining_stock(self, svc, item):
        """Void succeeds if enough stock remains (partial distribution only)."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        svc.process_distribution(item.id, quantity=3, reason_code=ReasonCode.CLIENT)

        # 7 units remain — voiding the 10-unit purchase requires 10, so should fail
        with pytest.raises(ValueError, match="Insufficient stock"):
            svc.void_transaction(tx.id, reason="Cannot void")


# ---------------------------------------------------------------------------
# Voiding a DONATION
# ---------------------------------------------------------------------------

class TestVoidDonation:
    """Voiding a donation removes the donated stock; cost basis is unaffected."""

    def test_void_donation_removes_stock(self, svc, item):
        """Stock drops back after voiding the donation."""
        _, tx = svc.process_donation(item.id, quantity=20, fair_market_value_dollars=1.00)

        updated_item, _orig, _corr = svc.void_transaction(tx.id, reason="Test void")

        assert updated_item.quantity_on_hand == 0

    def test_void_donation_cost_basis_unchanged(self, svc, item):
        """Voiding a donation does not change cost basis (donations are $0 cost)."""
        # First buy some stock to establish a cost basis
        svc.process_purchase(item.id, quantity=10, unit_cost_dollars=5.00)
        _, don_tx = svc.process_donation(item.id, quantity=10, fair_market_value_dollars=2.00)

        item_before = svc.get_item(item.id)
        cost_before = item_before.total_cost_basis_cents

        updated_item, _orig, _corr = svc.void_transaction(don_tx.id, reason="Test void")

        assert updated_item.total_cost_basis_cents == cost_before

    def test_void_donation_marks_original_voided(self, svc, item):
        """Original donation is marked voided."""
        _, tx = svc.process_donation(item.id, quantity=5, fair_market_value_dollars=1.00)

        _item, orig_tx, _corr = svc.void_transaction(tx.id, reason="Test void")

        assert orig_tx.is_voided is True

    def test_void_donation_insufficient_stock_raises(self, svc, item):
        """Cannot void a donation if that stock was already distributed."""
        _, tx = svc.process_donation(item.id, quantity=5, fair_market_value_dollars=1.00)
        svc.process_distribution(item.id, quantity=5, reason_code=ReasonCode.CLIENT)

        with pytest.raises(ValueError, match="Insufficient stock"):
            svc.void_transaction(tx.id, reason="Cannot void")


# ---------------------------------------------------------------------------
# Voiding a DISTRIBUTION
# ---------------------------------------------------------------------------

class TestVoidDistribution:
    """Voiding a distribution restores stock and the COGS that was deducted."""

    def test_void_distribution_restores_stock(self, svc, item):
        """Quantity returns to pre-distribution level after void."""
        svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        _, dist_tx = svc.process_distribution(item.id, quantity=4, reason_code=ReasonCode.CLIENT)

        updated_item, _orig, _corr = svc.void_transaction(dist_tx.id, reason="Test void")

        assert updated_item.quantity_on_hand == 10

    def test_void_distribution_restores_cost_basis(self, svc, item):
        """Cost basis is restored to pre-distribution amount after void."""
        svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        item_after_purchase = svc.get_item(item.id)
        original_cost_basis = item_after_purchase.total_cost_basis_cents

        _, dist_tx = svc.process_distribution(item.id, quantity=4, reason_code=ReasonCode.CLIENT)

        updated_item, _orig, _corr = svc.void_transaction(dist_tx.id, reason="Test void")

        assert updated_item.total_cost_basis_cents == original_cost_basis

    def test_void_distribution_marks_original_voided(self, svc, item):
        """Original distribution is marked voided."""
        svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        _, dist_tx = svc.process_distribution(item.id, quantity=4, reason_code=ReasonCode.CLIENT)

        _item, orig_tx, _corr = svc.void_transaction(dist_tx.id, reason="Test void")

        assert orig_tx.is_voided is True

    def test_void_distribution_creates_correction_referencing_original(self, svc, item):
        """Correction transaction references original distribution."""
        svc.process_purchase(item.id, quantity=10, unit_cost_dollars=2.00)
        _, dist_tx = svc.process_distribution(item.id, quantity=4, reason_code=ReasonCode.CLIENT)

        _item, _orig, corr_tx = svc.void_transaction(dist_tx.id, reason="Test void")

        assert corr_tx.ref_transaction_id == dist_tx.id


# ---------------------------------------------------------------------------
# Guard conditions
# ---------------------------------------------------------------------------

class TestVoidGuards:
    """Boundary conditions and error paths for void_transaction()."""

    def test_double_void_raises(self, svc, item):
        """Attempting to void an already-voided transaction raises ValueError."""
        _, tx = svc.process_purchase(item.id, quantity=10, unit_cost_dollars=1.00)
        svc.void_transaction(tx.id, reason="First void")

        with pytest.raises(ValueError, match="already voided"):
            svc.void_transaction(tx.id, reason="Second void")

    def test_void_nonexistent_transaction_raises(self, svc):
        """Voiding a transaction ID that doesn't exist raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            svc.void_transaction(transaction_id=99999, reason="No such tx")

    def test_void_returns_three_tuple(self, svc, item):
        """void_transaction returns (InventoryItem, orig_tx, correction_tx)."""
        _, tx = svc.process_purchase(item.id, quantity=5, unit_cost_dollars=1.00)
        result = svc.void_transaction(tx.id, reason="Return check")

        assert len(result) == 3
        updated_item, orig_tx, corr_tx = result
        # Types
        from models.item import InventoryItem
        from models.transaction import Transaction
        assert isinstance(updated_item, InventoryItem)
        assert isinstance(orig_tx, Transaction)
        assert isinstance(corr_tx, Transaction)
