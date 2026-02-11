# AIOps Studio - Inventory Development Log

**Project:** AIOps Studio - Inventory - Open Source Inventory System  
**Lead Developer:** Senior Python Developer  
**Started:** 2026-01-31

---

## Purpose

This development log tracks daily progress, technical decisions, challenges encountered, and solutions implemented during the AIOps Studio - Inventory development lifecycle. It serves as both a historical record and a knowledge base for future developers.

---

## Log Format

Each entry follows this structure:
- **Date:** YYYY-MM-DD
- **Phase:** Current development phase
- **Hours:** Time spent
- **Focus:** Main area of work
- **Accomplishments:** What was completed
- **Challenges:** Problems encountered
- **Solutions:** How challenges were resolved
- **Next Steps:** Planned work for next session
- **Notes:** Additional observations or decisions

---

## Development Entries

### 2026-02-07 | Database Path Fix & Rebranding

**Phase:** Development / Bug Fix  
**Focus:** Critical database initialization bug and application rebranding

#### Accomplishments
- 🐛 **Fixed critical database path bug**: `.exe` was creating `inventory.db` in local directory instead of `C:\Users\<user>\AppData\Local\AIOpsStudio\`
- 🔧 Updated `main.py` to initialize global `get_db_manager(db_path)` singleton **before** creating `MainWindow`
- 🏷️ Completed rebranding from "BlockTracker" to "AI OPS Studio"
- 🏷️ Renamed "Inventory" references to "BlockStock" where applicable

#### Bug Details
**Root Cause**: `main.py` computed the correct AppData database path but never passed it to services. When `InventoryService` called `get_db_manager()` without arguments, it defaulted to relative `"inventory.db"` — creating the file in the current working directory.

**Fix Applied**:
```python
# In main.py - BEFORE creating MainWindow
from database.connection import init_database, get_db_manager

# After computing db_path...
get_db_manager(db_path)  # Initialize singleton with correct path
```

This ensures all services that call `get_db_manager()` receive the already-initialized singleton pointing to AppData.

#### Technical Decisions
**Singleton Pattern for DatabaseManager**: The global `_db_manager` singleton pattern requires initialization order discipline. All database path setup must occur before any UI components are instantiated.

#### Next Steps
- Rebuild Windows `.exe` with the fix
- Test database loading with existing data in AppData
- Continue with Phase 1 MVP features

---

### 2026-02-10 | Phase 2 Completion - Efficiency Features

**Phase:** Phase 2: Efficiency
**Focus:** Dashboard, Visualization, and Data Import/Export

#### Accomplishments
- 📊 **Implemented Dashboard**: Created a real-time dashboard as the default landing page.
    - **KPI Cards**: Total Inventory Value, Low Stock Items, Total Items.
    - **Visualizations**: Added Matplotlib-based charts for "Value by Category" and "Top Distributed Items".
    - **Performance**: Optimized data retrieval with `ReportingService.get_dashboard_stats()`.
- 🔄 **Data Import/Export**:
    - **CSV Import**: Added functionality to bulk import items from CSV files.
    - **CSV Export**: Added functionality to export inventory items and transaction history.
    - **Service Layer**: Created `DataService` to handle CSV parsing and validation.
- 🎨 **UI Refinement**:
    - Integrated Dashboard into the main sidebar navigation.
    - Added "Import CSV" and "Export CSV" buttons to the Items Page header.
    - Verified `matplotlib` integration within PyQt6.

#### Technical Decisions
- **Matplotlib for Charts**: Chose standard `matplotlib` with `FigureCanvasQTAgg` backend for reliable, offline charting within PyQt6, avoiding the complexity of web-based graphing libraries.
- **DataService Separation**: Isolated CSV logic into `data_service.py` to keep `inventory_service.py` focused on core business logic.

#### Next Steps
- User review of Phase 2 features (Completed 2026-02-11).
- paused Phase 3 ("Connected") development pending user feedback.

---

### 2026-02-11 | Phase 2 Code Review & Refactoring

**Phase:** Start of Phase 3 Preparation
**Focus:** Code Quality, Logic Consistency, and Bug Fixes

#### Accomplishments
- 🧐 **Conducted Comprehensive Code Review**: Analyzed `src/` structure, logic, and tests.
- ♻️ **Refactored Inventory Logic**:
    - Moved weighted average cost calculation from `InventoryService` (inline) to `InventoryItem` (model method).
    - Eliminated logic duplication and ensured unit tests actually cover the running application's logic.
- 🐛 **Fixed CSV Export Bug**:
    - `DataService` now correctly fetches and maps Category IDs to Names (e.g., "Food", "Dry Goods") in exported CSVs.
- 🧹 **Cleanup**: Removed obsolete `uom` comments.

#### Technical Decisions
- **Model-Centric Logic**: Decided to encapsulate state-change logic (`calculate_purchase_state`) in the Model to enforce data integrity and simplify Service layer testing.

#### Next Steps
- Begin Phase 3: "Connected" features.

---

### 2026-02-11 | Dashboard Fixes & Maintenance

**Phase:** Phase 2 Polish / Maintenance
**Focus:** Dashboard Visualization Fixes, Build Validation, Project Cleanup

#### Accomplishments
- 📊 **Fixed Dashboard Charts**:
    - **Pie Chart**: Solved label overlapping issue by moving categories to a legend and hiding labels for small slices (< 5%).
    - **Bar Chart**: Fixed "blank" appearance and missing labels by implementing dynamic Y-axis scaling (1.2x max value).
- 📦 **Rebuilt Windows Executable**:
    - Validated build process with `build_windows.ps1`.
    - Generated new artifact in `dist/AIOpsStudio/AIOpsStudio.exe`.
- 🧹 **Project Cleanup**:
    - Audited project files and removed obsolete logs, temporary databases (`test_dashboard_*.db`), and legacy installer scripts (`BlockTracker.iss`).
    - Standardized on `AIOpsStudio.iss`.

#### Technical Decisions
- **Legend vs Labels**: For the pie chart, we switched from direct labeling (which caused collisions on small slices) to a side legend. This ensures readability regardless of data distribution.

#### Next Steps
- Begin Phase 3: "Connected" features.

---

### 2026-02-01 | Platform Refocus

**Phase:** Refactoring  
**Focus:** Windows 11 Fork  

#### Accomplishments
- 🧹 Removed MacOS specific code and build scripts
- 📝 Updated roadmap and README to reflect Windows-only scope
- 🔧 Hardcoded platform detection to Windows for performance and simplicity
- 🔄 Forked repository for Windows 11 optimization

#### Technical Decisions
**Windows-Only Architecture**: Decided to remove all cross-platform abstraction layers (Qt checks for MacOS menu bars, font selection logic) to streamline development for the primary target OS (Windows 11).

#### Next Steps
- Validate Windows build process
- Continue with Inventory Intake implementation


### 2026-01-31 | Project Initialization

**Phase:** Planning  
**Hours:** 2.5  
**Focus:** Project setup and planning documentation

#### Accomplishments
- ✅ Reviewed and analyzed Product Requirements Document (PRD)
- ✅ Created comprehensive `roadmap.md` with 3-phase development plan
- ✅ Created `devlog.md` for progress tracking
- ✅ Created `task.md` with detailed task breakdown
- ✅ Initialized `agents.md` for AI agent documentation
- ✅ Committed initial documentation to Git repository

#### Technical Decisions

##### Technology Stack Confirmation
After reviewing the PRD requirements, confirmed the following stack:
- **GUI Framework:** PyQt6 (chosen over PySide6 for better documentation and community support)
- **Database:** SQLite 3 (perfect for single-file, serverless requirements)
- **Reporting:** ReportLab (PDF) + Pandas (Excel)
- **Packaging:** PyInstaller (proven cross-platform support)

**Rationale:** This stack balances professional quality with ease of deployment for non-technical users.

##### Currency Storage Strategy
**Decision:** Store all currency values as **integers (cents)** in the database.

**Rationale:**
```python
# WRONG - Floating point drift
cost = 10.10 + 0.20  # May result in 10.299999999

# CORRECT - Integer arithmetic
cost_cents = 1010 + 20  # Always exactly 1030
cost_dollars = cost_cents / 100  # 10.30
```

This prevents the notorious floating-point precision errors that plague financial applications.

##### Weighted Average Cost Algorithm
**Decision:** Implement weighted average cost calculation at the transaction level.

**Formula:**
```
New_Avg_Cost = (Total_Cost_Basis + New_Incoming_Cost) / 
               (Total_Qty_On_Hand + New_Incoming_Qty)
```

**Example:**
```
Current State: 100 units @ $2.00/unit = $200 total
New Purchase: 50 units @ $3.00/unit = $150 total
New Average: ($200 + $150) / (100 + 50) = $2.33/unit
```

This ensures accurate COGS calculation when mixing donations ($0 cost) with purchases.

#### Project Structure Planning

Proposed directory structure:
```
AIOpsStudio-Inventory/
├── src/
│   ├── main.py                 # Application entry point
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── item.py
│   │   ├── transaction.py
│   │   └── category.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── inventory_service.py
│   │   ├── transaction_service.py
│   │   └── reporting_service.py
│   ├── ui/                     # PyQt6 interfaces
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── item_dialog.py
│   │   ├── intake_dialog.py
│   │   └── distribution_dialog.py
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations.py
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── platform_detect.py
│       └── validators.py
├── tests/                      # Test suite
│   ├── test_models.py
│   ├── test_services.py
│   └── test_integration.py
├── scripts/                    # Utility scripts
│   ├── init_db.py
│   └── create_sample_data.py
├── resources/                  # Assets
│   ├── icons/
│   └── styles/
├── docs/                       # Documentation
│   ├── user_manual.md
│   └── api_docs.md
├── requirements.txt
├── .gitignore
└── README.md
```

#### Challenges
None yet - planning phase went smoothly.

#### Next Steps
1. Set up Python virtual environment
2. Create project directory structure
3. Initialize Git repository with proper `.gitignore`
4. Create `requirements.txt` with pinned versions
5. Implement database schema from PRD Section 6
6. Write database initialization script

#### Notes
- Need to research PyQt6 best practices for cross-platform menu handling (macOS global menu bar vs Windows in-window menu)
- Should consider using SQLAlchemy ORM vs raw SQL - will evaluate in next session
- Need to set up CI/CD pipeline early for automated testing

---

### Template for Future Entries

```markdown
### YYYY-MM-DD | [Entry Title]

**Phase:** [Planning/Development/Testing/Deployment]  
**Hours:** [X.X]  
**Focus:** [Main area of work]

#### Accomplishments
- [ ] Item 1
- [ ] Item 2

#### Technical Decisions
[Any architectural or implementation decisions made]

#### Code Snippets
[Important code written or algorithms implemented]

#### Challenges
[Problems encountered]

#### Solutions
[How challenges were resolved]

#### Next Steps
[Planned work for next session]

#### Notes
[Additional observations]
```

---

## Key Metrics Tracking

### Development Velocity

| Week | Tasks Completed | Lines of Code | Tests Written | Bugs Fixed |
|------|----------------|---------------|---------------|------------|
| 1    | 5              | 0             | 0             | 0          |
| 2    | -              | -             | -             | -          |
| 3    | -              | -             | -             | -          |

### Code Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | 80% | 0% |
| Pylint Score | 9.0+ | - |
| Type Hint Coverage | 90% | - |
| Documentation Coverage | 100% | - |

### Performance Benchmarks

| Operation | Target | Current |
|-----------|--------|---------|
| Item Creation | < 100ms | - |
| Transaction Processing | < 200ms | - |
| Report Generation | < 5s | - |
| Database Query (1000 items) | < 50ms | - |

---

## Technical Debt Log

### Current Debt
*None yet - project just started*

### Resolved Debt
*N/A*

---

## Learning & Research Notes

### PyQt6 Cross-Platform Considerations

**macOS Specific:**
- Use `QMenuBar` with `setNativeMenuBar(True)` for global menu bar
- Keyboard shortcuts use `Cmd` instead of `Ctrl`
- Window controls (traffic lights) are top-left by default
- Use SF Pro font family

**Windows Specific:**
- Menu bar embedded in window
- Keyboard shortcuts use `Ctrl`
- Window controls (minimize/maximize/close) are top-right
- Use Segoe UI font family

**Cross-Platform Detection:**
```python
import platform

def get_platform():
    system = platform.system()
    if system == 'Darwin':
        return 'macos'
    elif system == 'Windows':
        return 'windows'
    elif system == 'Linux':
        return 'linux'
    return 'unknown'
```

### SQLite Best Practices for Inventory Systems

1. **Use WAL Mode** for better concurrency:
   ```sql
   PRAGMA journal_mode=WAL;
   ```

2. **Enable Foreign Keys** (disabled by default):
   ```sql
   PRAGMA foreign_keys=ON;
   ```

3. **Regular VACUUM** to reclaim space:
   ```sql
   VACUUM;
   ```

4. **Use Transactions** for multi-step operations:
   ```python
   with connection:
       cursor.execute("INSERT INTO ...")
       cursor.execute("UPDATE ...")
   ```

---

## Bug Tracker

### Open Bugs
*None yet*

### Resolved Bugs
*N/A*

---

## Feature Requests & Ideas

### From Stakeholders
*To be collected during user testing*

### Developer Ideas
- Consider adding a "Quick Distribution" mode for high-volume days
- Implement keyboard shortcuts for power users (e.g., Ctrl+N for new item)
- Add dark mode support for better accessibility
- Consider internationalization (i18n) for future Spanish language support

---

## Meeting Notes

### Stakeholder Meetings
*No meetings yet*

### Code Review Sessions
*No reviews yet*

---

## Resources & References

### Helpful Articles
- [PyQt6 Tutorial](https://www.pythonguis.com/pyqt6-tutorial/)
- [SQLite Performance Tuning](https://www.sqlite.org/speed.html)
- [Weighted Average Cost Accounting](https://www.investopedia.com/terms/w/weightedaverage.asp)

### Code Examples
- [PyQt6 Cross-Platform Menu Example](https://github.com/pyqt/examples)
- [SQLite Transaction Patterns](https://sqlite.org/lang_transaction.html)

---

## Retrospectives

### What Went Well
*To be filled after each milestone*

### What Could Be Improved
*To be filled after each milestone*

### Action Items
*To be filled after each milestone*

---

**Last Updated:** 2026-01-31  
**Next Review:** 2026-02-07 (Weekly)
