"""
Tests for DataService CSV import and export.

Covers:
- CSV import: valid data (qty + cost recorded as PURCHASE)
- CSV import: currency-symbol stripping ($10.00)
- CSV import: zero-quantity rows (item created, no purchase)
- CSV import: category ID column resolution
- CSV import: category name column resolution (auto-creates category)
- CSV import: duplicate SKU increments fail count
- CSV import: missing required columns returns error list
- CSV export: produces file with expected headers
- export_transactions_to_csv: produces file with data
"""

import csv
import io
from pathlib import Path

import pytest

from services.inventory_service import InventoryService
from services.data_service import DataService


# ---------------------------------------------------------------------------
# Helper – write a CSV string to a temp file and return the path
# ---------------------------------------------------------------------------

def _write_csv(tmp_path: Path, filename: str, rows: list) -> str:
    """Write a list-of-lists CSV to a temp file. First row is the header."""
    p = tmp_path / filename
    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return str(p)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc():
    """InventoryService backed by the isolated in-memory DB."""
    return InventoryService()


@pytest.fixture
def data_svc(svc):
    """DataService wrapping the in-memory InventoryService."""
    return DataService(svc)


# ---------------------------------------------------------------------------
# CSV Import — happy-path
# ---------------------------------------------------------------------------

class TestCSVImportHappyPath:

    def test_import_returns_success_count(self, data_svc, tmp_path):
        """Four valid rows → success count == 4."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["A001", "Alpha",   "10", "1.00"],
            ["B001", "Bravo",   "20", "2.50"],
            ["C001", "Charlie",  "5", "0.75"],
            ["D001", "Delta",    "0", "0.00"],
        ])
        success, fail, errors = data_svc.import_items_from_csv(csv_file)
        assert success == 4
        assert fail == 0
        assert errors == []

    def test_import_creates_items_in_db(self, data_svc, svc, tmp_path):
        """Imported SKUs are retrievable from the database."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["X001", "X-Ray", "5", "3.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("X001")
        assert item is not None
        assert item.name == "X-Ray"

    def test_import_quantity_recorded_as_purchase(self, data_svc, svc, tmp_path):
        """Rows with quantity > 0 result in the correct stock level."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["Q001", "Qty Item", "42", "1.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("Q001")
        assert item.quantity_on_hand == 42.0

    def test_import_unit_cost_recorded(self, data_svc, svc, tmp_path):
        """Unit cost is stored correctly on the item."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["P001", "Priced Item", "10", "5.50"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("P001")
        assert item.current_unit_cost_dollars == 5.50

    def test_import_zero_quantity_no_purchase(self, data_svc, svc, tmp_path):
        """Rows with quantity == 0 create the item but no purchase transaction."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["Z001", "Zero Item", "0", "0.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("Z001")
        assert item is not None
        assert item.quantity_on_hand == 0.0
        history = svc.get_item_transactions(item.id)
        assert history == []


# ---------------------------------------------------------------------------
# CSV Import — currency symbol stripping
# ---------------------------------------------------------------------------

class TestCSVImportCurrencyParsing:

    def test_dollar_sign_stripped_from_unit_cost(self, data_svc, svc, tmp_path):
        """Unit Cost column values with leading $ are parsed correctly."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["DS001", "Dollar Sign Item", "10", "$12.99"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("DS001")
        assert item.current_unit_cost_dollars == 12.99

    def test_comma_stripped_from_quantity(self, data_svc, svc, tmp_path):
        """Quantity values with comma-thousands separators are parsed correctly."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["CS001", "Comma Sep Item", "1,000", "1.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("CS001")
        assert item.quantity_on_hand == 1000.0


# ---------------------------------------------------------------------------
# CSV Import — category resolution
# ---------------------------------------------------------------------------

class TestCSVImportCategoryResolution:

    def test_category_id_column_resolved(self, data_svc, svc, tmp_path):
        """Items with a numeric Category ID column get the correct category_id."""
        # Create a category first
        conn = svc.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO item_categories (name) VALUES ('Produce')")
        conn.commit()
        cat_id = cursor.lastrowid

        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Category ID", "Quantity", "Unit Cost ($)"],
            ["CAT001", "Cat Item", str(cat_id), "5", "1.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("CAT001")
        assert item.category_id == cat_id

    def test_category_name_column_matches_existing(self, data_svc, svc, tmp_path):
        """Items with a Category name column matching an existing category are linked."""
        conn = svc.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO item_categories (name) VALUES ('Bakery')")
        conn.commit()
        bakery_id = cursor.lastrowid

        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Category", "Quantity", "Unit Cost ($)"],
            ["BKY001", "Bread", "Bakery", "10", "2.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("BKY001")
        assert item.category_id == bakery_id

    def test_category_name_column_creates_new_category(self, data_svc, svc, tmp_path):
        """Unknown category names are auto-created and the item is linked."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Category", "Quantity", "Unit Cost ($)"],
            ["NEW001", "New Cat Item", "SpecialGoods", "5", "1.00"],
        ])
        data_svc.import_items_from_csv(csv_file)
        item = svc.get_item_by_sku("NEW001")
        assert item is not None
        assert item.category_id is not None

        # Verify the new category actually exists
        categories = svc.get_all_categories()
        cat_names = [c.name for c in categories]
        assert "SpecialGoods" in cat_names


# ---------------------------------------------------------------------------
# CSV Import — error handling
# ---------------------------------------------------------------------------

class TestCSVImportErrors:

    def test_duplicate_sku_increments_fail_count(self, data_svc, svc, tmp_path):
        """A row whose SKU already exists is counted as a failure."""
        svc.create_item(sku="DUP001", name="Existing")

        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Name", "Quantity", "Unit Cost ($)"],
            ["DUP001", "Duplicate", "5", "1.00"],
            ["NEW999", "New Item",  "5", "1.00"],
        ])
        success, fail, errors = data_svc.import_items_from_csv(csv_file)

        assert fail == 1
        assert success == 1
        assert any("DUP001" in e for e in errors)

    def test_missing_sku_column_returns_error(self, data_svc, tmp_path):
        """Missing required SKU column returns an immediate error, zero rows imported."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["Name", "Quantity"],
            ["No SKU Item", "5"],
        ])
        success, fail, errors = data_svc.import_items_from_csv(csv_file)

        assert success == 0
        assert any("sku" in e.lower() for e in errors)

    def test_missing_name_column_returns_error(self, data_svc, tmp_path):
        """Missing required Name column returns an immediate error."""
        csv_file = _write_csv(tmp_path, "items.csv", [
            ["SKU", "Quantity"],
            ["NO_NAME", "5"],
        ])
        success, fail, errors = data_svc.import_items_from_csv(csv_file)

        assert success == 0
        assert any("name" in e.lower() for e in errors)

    def test_nonexistent_file_returns_error(self, data_svc):
        """Providing a path to a non-existent file returns a file error."""
        success, fail, errors = data_svc.import_items_from_csv("/no/such/file.csv")

        assert success == 0
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# CSV Export — items
# ---------------------------------------------------------------------------

class TestCSVExport:

    def test_export_items_creates_file(self, data_svc, svc, tmp_path):
        """export_items_to_csv creates the output file."""
        svc.create_item(sku="EXP001", name="Export Me")
        out_file = str(tmp_path / "export.csv")

        result = data_svc.export_items_to_csv(out_file)

        assert result is True
        assert Path(out_file).exists()

    def test_export_items_has_expected_headers(self, data_svc, svc, tmp_path):
        """Exported CSV contains the standard header row."""
        svc.create_item(sku="EXP002", name="Header Check")
        out_file = str(tmp_path / "export.csv")
        data_svc.export_items_to_csv(out_file)

        with open(out_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = [h.lower() for h in next(reader)]

        assert "sku" in headers
        assert "name" in headers

    def test_export_items_contains_data_rows(self, data_svc, svc, tmp_path):
        """Exported CSV contains one data row per active item."""
        svc.create_item(sku="EXP003", name="Data Row A")
        svc.create_item(sku="EXP004", name="Data Row B")
        out_file = str(tmp_path / "export.csv")
        data_svc.export_items_to_csv(out_file)

        with open(out_file, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

        # 1 header + at least 2 data rows
        assert len(rows) >= 3

    def test_export_items_returns_false_on_bad_path(self, data_svc):
        """export_items_to_csv returns False when the destination is invalid."""
        result = data_svc.export_items_to_csv("/no/such/directory/out.csv")
        assert result is False


# ---------------------------------------------------------------------------
# CSV Export — transactions
# ---------------------------------------------------------------------------

class TestCSVExportTransactions:

    def test_export_transactions_creates_file(self, data_svc, svc, tmp_path):
        """export_transactions_to_csv creates the output file."""
        item = svc.create_item(sku="TX001", name="Tx Export Item")
        svc.process_purchase(item.id, quantity=5, unit_cost_dollars=2.00)
        out_file = str(tmp_path / "transactions.csv")

        result = data_svc.export_transactions_to_csv(out_file)

        assert result is True
        assert Path(out_file).exists()

    def test_export_transactions_has_expected_headers(self, data_svc, svc, tmp_path):
        """Transaction export CSV contains standard header columns."""
        item = svc.create_item(sku="TX002", name="Tx Header Check")
        svc.process_purchase(item.id, quantity=5, unit_cost_dollars=2.00)
        out_file = str(tmp_path / "transactions.csv")
        data_svc.export_transactions_to_csv(out_file)

        with open(out_file, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = [h.lower() for h in next(reader)]

        assert "sku" in headers
        assert "type" in headers or any("type" in h for h in headers)
