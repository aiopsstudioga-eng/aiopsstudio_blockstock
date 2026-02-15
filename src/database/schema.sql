-- AIOps Studio - Inventory Database Schema
-- Version: 1.0
-- Database: SQLite 3

-- Enable Foreign Keys (must be set per connection)
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- ============================================================================
-- TABLE: item_categories
-- Purpose: Hierarchical categorization of inventory items
-- ============================================================================
CREATE TABLE IF NOT EXISTS item_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    parent_id INTEGER,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES item_categories(id)
);

-- ============================================================================
-- TABLE: inventory_items
-- Purpose: Current state snapshot of all inventory items
-- Note: Uses weighted average cost accounting
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER,
    -- uom column removed
    quantity_on_hand REAL DEFAULT 0,
    reorder_threshold INTEGER DEFAULT 10,
    total_cost_basis_cents INTEGER DEFAULT 0,  -- Total actual money invested (in cents)
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES item_categories(id),
    CHECK (quantity_on_hand >= 0),
    CHECK (total_cost_basis_cents >= 0)
);

-- ============================================================================
-- TABLE: inventory_transactions
-- Purpose: Immutable audit log of all inventory movements
-- Transaction Types:
--   - PURCHASE: Bought items (has unit_cost > 0)
--   - DONATION: Received donated items (unit_cost = 0, has fair_market_value)
--   - DISTRIBUTION: Items given out (negative quantity_change)
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,  -- 'PURCHASE', 'DONATION', 'DISTRIBUTION'
    quantity_change REAL NOT NULL,  -- Positive for intake, negative for distribution
    unit_cost_cents INTEGER DEFAULT 0,  -- Actual cost per unit (0 for donations)
    fair_market_value_cents INTEGER DEFAULT 0,  -- For impact reports (donations)
    total_financial_impact_cents INTEGER DEFAULT 0,  -- COGS impact (for distributions)
    reason_code TEXT,  -- For distributions: 'CLIENT', 'SPOILAGE', 'INTERNAL'
    supplier TEXT,  -- For purchases
    donor TEXT,  -- For donations
    notes TEXT,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',
    is_voided BOOLEAN DEFAULT 0,
    ref_transaction_id INTEGER,
    FOREIGN KEY (item_id) REFERENCES inventory_items(id),
    FOREIGN KEY (ref_transaction_id) REFERENCES inventory_transactions(id),
    CHECK (transaction_type IN ('PURCHASE', 'DONATION', 'DISTRIBUTION', 'CORRECTION')),
    CHECK (
        (transaction_type = 'DISTRIBUTION' AND quantity_change < 0) OR
        (transaction_type IN ('PURCHASE', 'DONATION') AND quantity_change > 0) OR
        (transaction_type = 'CORRECTION' AND quantity_change != 0)
    )
);

-- ============================================================================
-- INDEXES for Performance Optimization
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_items_sku ON inventory_items(sku);
CREATE INDEX IF NOT EXISTS idx_items_category ON inventory_items(category_id);
CREATE INDEX IF NOT EXISTS idx_items_active ON inventory_items(is_active);
CREATE INDEX IF NOT EXISTS idx_trans_item ON inventory_transactions(item_id);
CREATE INDEX IF NOT EXISTS idx_trans_date ON inventory_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_trans_type ON inventory_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_trans_voided ON inventory_transactions(is_voided);

-- ============================================================================
-- TRIGGERS for Automatic Timestamp Updates
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS update_item_timestamp 
AFTER UPDATE ON inventory_items
BEGIN
    UPDATE inventory_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- SEED DATA: Default Categories
-- ============================================================================
INSERT OR IGNORE INTO item_categories (id, name, parent_id, description) VALUES
(1, 'Food', NULL, 'All food items'),
(2, 'Non-Food', NULL, 'Non-food items'),
(3, 'Canned Goods', 1, 'Canned food items'),
(4, 'Dry Goods', 1, 'Dry food items'),
(5, 'Fresh Produce', 1, 'Fresh fruits and vegetables'),
(6, 'Frozen', 1, 'Frozen food items'),
(7, 'Hygiene', 2, 'Personal hygiene products'),
(8, 'Cleaning', 2, 'Cleaning supplies'),
(9, 'Paper Products', 2, 'Paper towels, toilet paper, etc.');
