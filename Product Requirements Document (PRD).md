# Product Requirements Document (PRD)
**Project Name:** PantryTracker (Open Source Inventory System)
**Version:** 1.0 (MVP)
**Status:** APPROVED FOR DEVELOPMENT
**Author:** Senior Product Manager

# 1\. Executive Summary
**Vision:** To provide non-profit food pantries with a professional-grade, cross-platform desktop application that accurately tracks inventory levels while solving the complex accounting challenge of mixing "Zero-Cost" (Donated) goods with "Purchased" goods.
**Core Problem:** Generic inventory systems assume all items have a purchase cost. Food pantries operate on a mix of purchased goods (Cost > $0) and donations (Cost = $0), making it impossible to calculate accurate "Cost of Goods Sold" (COGS) or "Asset Value" without manual spreadsheet manipulation.
**Success Metrics:**
1. **Financial Accuracy:** End-of-month financial reports generated in < 5 seconds with 100% mathematical accuracy on weighted averages.
2. **Usability:** Volunteer onboarding time < 15 minutes.
3. **Stability:** Zero data corruption incidents on local SQLite database.

⠀
# 2\. User Personas
| **Persona** | **Role** | **Tech Proficiency** | **Primary Goal** | **Pain Point** |
|---|---|---|---|---|
| **Margaret (The Manager)** | Administrator | Moderate (Excel user) | Generate reports for the Board; Track budget vs. impact. | Currently spends 4 hours/month fixing broken Excel formulas. |
| **Sam (The Volunteer)** | Operator | Low to Variable | Check-in donations and log distributions quickly. | Afraid of "deleting everything" by accident; confused by complex menus. |

# 3\. Functional Requirements
### 3.1 Module: Item Master Management
* **FR-01 (Create/Edit):** System shall allow creation of items with: Name, SKU (Manual/Barcode), Category, Unit of Measure (UOM), and Reorder Threshold.
* **FR-02 (Soft Delete):** Items cannot be hard-deleted if they have transaction history. They must be flagged is_active = False.
* **FR-03 (Categorization):** Support for 2-level hierarchy (Category -> Item). *Example: Food -> Canned Vegetables -> Green Beans.*

⠀3.2 Module: Inventory Intake (The Core Differentiator)
* **FR-04 (Dual Source Logic):**
  * **Mode A: Purchase:** User inputs Supplier, Qty, and **Unit Cost ($)**. System updates Total Cost Basis.
  * **Mode B: Donation:** User inputs Donor (Optional), Qty, and **Fair Market Value ($)**. System records Value for "Impact Reports" but sets **Unit Cost to $0.00** for "Financial Reports."
* **FR-05 (Visual Cues):** Interface must visually distinguish modes (e.g., Green background for Donations, Blue for Purchases).

⠀3.3 Module: Distribution & Output
* **FR-06 (Usage Logging):** User selects items and Reason Code (Client Distribution, Spoilage, Internal Use).
* **FR-07 (Validation):** System prevents distributing more quantity than exists in quantity_on_hand.
* **FR-08 (Cost Depletion):** System calculates the value of removed items based on the **Current Weighted Average Cost** at the moment of the transaction.

⠀3.4 Module: Reporting & Analytics
* **FR-09 (Financial Report):** "Cost of Goods Distributed" – Calculates real money spent on items given away.
* **FR-10 (Impact Report):** "Total Value Distributed" – Calculates Fair Market Value of items given away (used for donor newsletters).
* **FR-11 (Stock Status):** List of items below reorder_threshold.

⠀
# 4\. UX & Cross-Platform Design Guidelines
The application must feel "Native" on both platforms. We will use **PyQt6** or **PySide6**.
### 4.1 Windows Implementation
* **Window Controls:** Standard Top-Right (Minimize, Maximize, Close).
* **Navigation:** Left-hand vertical Sidebar (Accordion style).
* **Typography:** Segoe UI.

⠀4.2 macOS Implementation
* **Window Controls:** Traffic lights (Top-Left).
* **Menu Bar:** Global Menu Bar integration (File, Edit, View, Help). *Do not put a hamburger menu inside the window.*
* **Typography:** San Francisco (SF Pro).
* **Shortcuts:** Use Cmd instead of Ctrl for shortcuts (e.g., Cmd+S to save).

⠀4.3 Accessibility (Required)
* **Contrast:** WCAG AA compliant text contrast.
* **Tab Order:** Logical tab indexing for keyboard-only data entry.
* **Font Sizing:** Support for system-level font scaling.

⠀
# 5\. Technical Architecture
### 5.1 Technology Stack
* **Language:** Python 3.10+
* **GUI Framework:** PyQt6 (Stable, professional, rich widget set).
* **Database:** SQLite 3 (Serverless, single-file).
* **Reporting Engine:** ReportLab (PDF) + Pandas (Excel Export).
* **Packaging:** PyInstaller (creates .exe and .app).
* ![](Product%20Requirements%20Document%20%28PRD%29/licensed-image.jpg)Getty ImagesExplore 

⠀5.2 The Accounting Logic (Weighted Average Cost)
* **Formula:** New_Avg_Cost = (Total_Cost_Basis + New_Incoming_Cost) / (Total_Qty_On_Hand + New_Incoming_Qty)
* **Constraint:** All currency values must be stored as **Integers (Cents)** in the database to prevent floating-point drift.

⠀
# 6\. Database Schema (SQLite)
This schema is designed for immutable audit logging.
SQL

-- 1. ITEMS TABLE (Current State Snapshot)
CREATE TABLE inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER,
    uom TEXT DEFAULT 'Unit',
    quantity_on_hand REAL DEFAULT 0,
    reorder_threshold INTEGER DEFAULT 10,
    total_cost_basis_cents INTEGER DEFAULT 0, -- Total actual money invested
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES item_categories(id)
);

-- 2. TRANSACTIONS TABLE (Immutable History)
CREATE TABLE inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- 'PURCHASE', 'DONATION', 'DISTRIBUTION'
    quantity_change REAL NOT NULL,
    unit_cost_cents INTEGER DEFAULT 0, -- Actual Cost (0 for donations)
    fair_market_value_cents INTEGER DEFAULT 0, -- For Impact Reports
    total_financial_impact_cents INTEGER DEFAULT 0, -- COGS impact
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory_items(id)
);

-- Indexes for Performance
CREATE INDEX idx_items_sku ON inventory_items(sku);
CREATE INDEX idx_trans_date ON inventory_transactions(transaction_date);

# 7\. Roadmap & Prioritization
### Phase 1: MVP (The "Paper Killer")
* **Goal:** Replace the manual binder/Excel sheet.
* **Features:**
  * Manual Item Creation.
  * Manual Intake (Donation vs Purchase forms).
  * Manual Distribution.
  * Basic PDF Report (Current Inventory Value).
  * Database Backup (Export .db file).

⠀Phase 2: Efficiency (Post-Launch)
* **Goal:** Speed up data entry.
* **Features:**
  * USB Barcode Scanner Integration (HID Mode).
  * Dashboard Charts (Visualizing trends).
  * Import from CSV (for initial migration).

⠀Phase 3: Connected (Future)
* **Goal:** Remote safety.
* **Features:**
  * Google Drive / Dropbox API integration for auto-backups.
  * Email SMTP integration to email reports directly to Board Members.

⠀
### 8\. Engineering Handoff Checklist
1. [ ] Set up Virtual Environment (venv).
2. [ ] Install PyQt6 and sqlite3.
3. [ ] Initialize Database using the Schema provided in Section 6.
4. [ ] Implement the InventoryItem class logic (specifically the intake_stock method handles the weighted average math).
