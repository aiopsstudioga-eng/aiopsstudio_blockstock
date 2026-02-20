# AIOps Studio - Inventory Development Roadmap

**Project:** AIOps Studio - Inventory - Open Source Inventory System for Food Pantries  
**Version:** 1.0 MVP  
**Last Updated:** 2026-02-19  
**Status:** Phase 2 Complete - QA & Bug Fixes Complete - Preparing Phase 3

---

## 🎯 Project Vision

Build a professional-grade Windows 11 application that solves the unique inventory accounting challenge faced by non-profit food pantries: accurately tracking mixed "Zero-Cost" (donated) and "Purchased" goods while maintaining financial accuracy for COGS reporting.

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Financial Accuracy** | 100% mathematical accuracy | Automated tests on weighted average calculations |
| **Report Generation Speed** | < 5 seconds | End-of-month financial reports |
| **Volunteer Onboarding** | < 15 minutes | Time to first successful transaction |
| **Data Integrity** | Zero corruption incidents | SQLite database reliability |
| **Platform** | Windows 11+ | Native look and feel |

---

## 🗺️ Development Phases

### **Phase 1: MVP - "The Paper Killer"** ✅ *Complete*

**Timeline:** 8-10 weeks  
**Goal:** Replace manual binder/Excel sheet with reliable desktop application

#### Core Deliverables

```mermaid
graph LR
    A[Item Master] --> B[Inventory Intake]
    B --> C[Distribution]
    C --> D[Reporting]
    D --> E[Backup]
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#e1f5ff
    style E fill:#e1f5ff
```

#### Feature Breakdown

##### 1. Foundation (Week 1-2)

- [x] Project structure setup
- [x] Virtual environment configuration
- [x] Dependency installation (PyQt6, SQLite3, ReportLab, Pandas)
- [x] Database schema implementation
- [x] Windows environment configuration
- [x] Git repository initialization

##### 2. Item Master Management (Week 2-3)

- [x] Create/Edit/View items interface
- [x] SKU and barcode input support
- [x] 2-level category hierarchy
- [x] Unit of Measure (UOM) selection
- [x] Reorder threshold configuration
- [x] Soft delete implementation (preserve transaction history)

##### 3. Inventory Intake - The Differentiator (Week 3-5)

- [x] **Purchase Mode** (Blue UI)
  - Supplier tracking
  - Quantity input
  - Unit cost entry
  - Total cost basis update
  
- [x] **Donation Mode** (Green UI)
  - Optional donor tracking
  - Quantity input
  - Fair market value entry
  - Zero-cost accounting logic

- [x] **Weighted Average Cost Engine**

  ```python
  # Core Formula Implementation
  new_avg_cost = (total_cost_basis + new_incoming_cost) / 
                 (qty_on_hand + new_incoming_qty)
  ```

  - Integer-based currency (cents) to prevent floating-point drift
  - Real-time cost basis updates
  - Audit trail for all cost changes

##### 4. Distribution & Output (Week 5-6)

- [x] Distribution interface with reason codes:
  - Client Distribution
  - Spoilage
  - Internal Use
- [x] Quantity validation (prevent negative inventory)
- [x] COGS calculation at weighted average cost
- [x] Transaction confirmation dialogs
- [x] Undo functionality for recent transactions (Void/Correction workflow)
- [x] Global exception handler for crash protection
- [x] Training Mode with production cloning
- [x] Opening balance transactions for training mode

##### 5. Reporting & Analytics (Week 6-8)

- [x] **Financial Report** - "Cost of Goods Distributed"
  - Real money spent on distributed items
  - Monthly/Quarterly/Annual views
  - PDF export via ReportLab
  
- [x] **Impact Report** - "Total Value Distributed"
  - Fair market value for donor newsletters
  - Donation vs. Purchase breakdown
  - Excel export via Pandas
  
- [x] **Stock Status Report**
  - Items below reorder threshold
  - Zero-stock alerts
  - Category-based filtering
- [x] Transaction history with void/correction support

##### 6. Windows UI Polish (Week 8-9)

- [x] **Windows Implementation**
  - Segoe UI typography
  - Standard window controls (top-right)
  - Vertical sidebar navigation
- [x] Main window with sidebar navigation
- [x] Dashboard page with KPI cards
- [x] Items page with search and filtering

##### 7. Testing & Packaging (Week 9-10)

- [x] Unit tests (55+ tests passing)
- [x] Integration tests
- [x] Windows testing
- [x] PyInstaller configuration
  - Windows .exe bundle
- [x] User documentation
- [x] Sample database with demo data (Training Mode Seeder with Production Cloning)

---

### **Phase 2: Efficiency** ✅ *Complete*

**Timeline:** 4-6 weeks (Post-MVP Launch)  
**Goal:** Speed up data entry and improve user experience

#### Features

##### Dashboard & Visualization

- [x] Real-time inventory value chart
- [x] Distribution trends (weekly/monthly)
- [x] Top distributed items
- [x] Donation vs. Purchase ratio visualization
- [x] Interactive charts using Matplotlib

##### Data Import/Export

- [x] CSV import for initial migration
- [x] Bulk item creation
- [x] Transaction history export
- [x] SKU autocomplete (type-ahead search)
- [x] Category auto-creation during CSV import
- [x] CSV export with category names (not IDs)
- [ ] Backup scheduling system

##### Performance Optimization

- [x] Database indexing optimization (idx_trans_voided)
- [ ] Lazy loading for large datasets
- [ ] Query caching
- [ ] Background task processing

---

### **Phase: QA & Bug Fixes** ✅ *Complete*

**Timeline:** 2026-02-14 to 2026-02-19  
**Goal:** Code quality, stability, and critical bug fixes

#### Critical Fixes (P1)

- [x] Voided transactions excluded from financial reports
- [x] Exception hook registered before window.show()
- [x] Tooltip bug on Production Mode button fixed
- [x] SQL injection via string-interpolated LIMIT fixed

#### High Priority Fixes (P2)

- [x] DatabaseManager singleton initialization enforcement
- [x] WAL-safe backup using SQLite backup API
- [x] BaseIntakeDialog refactor (eliminated code duplication)
- [x] Integer rounding fixed (now uses round() for cost calculations)
- [x] SKU search fix (parse SKU from "SKU — Name" display string)

#### Testing

- [x] 55 tests passing (void workflow + data service tests)
- [x] Test isolation with isolated_db autouse fixture
- [x] Void workflow test suite (17 tests)
- [x] DataService test suite (20 tests)

#### Infrastructure

- [x] Centralized logging system (rotating file handler)
- [x] Error handler utilities with dialogs
- [x] Production database path fix (.exe now uses AppData)
- [x] Consolidated duplicate transaction history methods
- [x] Datetime adapter fix for Python 3.12+ compatibility

---

### **Phase 3: Connected** 🔜 *Next Phase*

**Timeline:** 6-8 weeks (Future Enhancement)  
**Goal:** Remote safety and collaboration features

#### Features

##### Cloud Backup Integration

- [ ] Google Drive API integration
- [ ] Dropbox API integration
- [ ] Automatic daily backups
- [ ] Backup restoration wizard
- [ ] Conflict resolution

##### Email Automation

- [ ] SMTP configuration
- [ ] Automated monthly reports to board members
- [ ] Low-stock email alerts
- [ ] Donation receipt generation

##### Multi-User Considerations

- [ ] User authentication system
- [ ] Role-based permissions (Admin, Volunteer, View-Only)
- [ ] Audit log for user actions
- [ ] Concurrent access handling

##### Advanced Analytics

- [x] Predictive inventory forecasting
- [x] Seasonal trend analysis
- [x] Donor impact tracking
- [ ] Budget vs. actual spending reports (Not applicable - no budget data)

---

## 🏗️ Technical Architecture

### Technology Stack

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[PyQt6 GUI]
        B[Platform Detection]
    end
    
    subgraph "Business Logic Layer"
        C[Inventory Service]
        D[Transaction Service]
        E[Reporting Service]
    end
    
    subgraph "Data Layer"
        F[SQLite Database]
        G[Backup Manager]
    end
    
    subgraph "External Services"
        H[ReportLab - PDF]
        I[Pandas - Excel]
    end
    
    A --> C
    A --> D
    A --> E
    C --> F
    D --> F
    E --> F
    E --> H
    E --> I
    F --> G
    
    style A fill:#4CAF50
    style C fill:#2196F3
    style F fill:#FF9800
```

### Core Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **GUI Framework** | PyQt6 | Windows native UI |
| **Database** | SQLite 3 | Serverless, single-file storage |
| **PDF Generation** | ReportLab | Financial reports |
| **Excel Export** | Pandas | Data analysis and export |
| **Packaging** | PyInstaller | Standalone executables |
| **Testing** | pytest | Unit and integration tests |
| **Version Control** | Git | Source code management |

---

## 🎓 Best Practices & Standards

### Code Quality

- **PEP 8** compliance for all Python code
- **Type hints** for function signatures
- **Docstrings** for all public methods
- **Unit tests** with 80%+ coverage
- **Code reviews** before merging

### Database Design

- **Immutable audit logging** - never delete transaction records
- **Integer currency storage** - prevent floating-point errors
- **Foreign key constraints** - maintain referential integrity
- **Indexed queries** - optimize performance
- **Regular backups** - prevent data loss

### Security

- **SQL injection prevention** - parameterized queries only
- **Input validation** - sanitize all user inputs
- **Error handling** - graceful degradation
- **Audit logging** - track all data modifications
- **Data encryption** - for sensitive information (Phase 3)

### User Experience

- **Consistent terminology** - use domain language
- **Visual feedback** - loading indicators, success/error messages
- **Keyboard shortcuts** - power user efficiency
- **Undo functionality** - prevent user mistakes
- **Contextual help** - tooltips and documentation

---

## 📅 Milestone Schedule

| Milestone | Target Date | Deliverables |
|-----------|-------------|--------------|
| **M1: Foundation** | Week 2 | Database schema, project structure, dev environment |
| **M2: Core CRUD** | Week 4 | Item management, basic intake/distribution |
| **M3: Accounting Engine** | Week 6 | Weighted average cost, dual-mode intake |
| **M4: Reporting** | Week 8 | Financial & Impact reports, PDF/Excel export |
| **M5: MVP Release** | Week 10 | Windows builds, documentation, testing complete |
| **M6: Efficiency Features** | Week 16 | Dashboard, CSV import, performance optimization |
| **M7: Connected Features** | Week 24 | Cloud backup, email automation, multi-user |

---

## 🚧 Risk Management

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Floating-point precision errors** | High | Use integer cents for all currency |
| **Windows UI inconsistencies** | Low | Standard Windows controls, Segoe UI |
| **Database corruption** | High | Automated backups, transaction rollback |
| **PyInstaller compatibility issues** | Medium | Early packaging tests, dependency pinning |
| **Performance with large datasets** | Low | Database indexing, pagination, lazy loading |

### User Adoption Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Volunteer resistance to change** | High | Simple UI, extensive training, gradual rollout |
| **Data migration errors** | High | CSV import tool, validation, rollback capability |
| **Learning curve too steep** | Medium | Video tutorials, in-app help, tooltips |
| **Missing critical features** | Medium | User feedback sessions, iterative development |

---

## 🔄 Feedback & Iteration

### User Testing Checkpoints

- **Week 4:** Item management UI testing with Margaret (Manager persona)
- **Week 6:** Intake workflow testing with Sam (Volunteer persona)
- **Week 8:** Report generation testing with Board members
- **Week 10:** Full system UAT with pilot pantry

### Success Criteria for MVP Launch

- [ ] All Phase 1 features implemented and tested
- [ ] Zero critical bugs in issue tracker
- [ ] User documentation complete
- [ ] Successful deployment at 1 pilot location
- [ ] Positive feedback from both personas (Margaret & Sam)
- [ ] Financial reports match manual Excel calculations

---

## 📚 Resources & References

### Development Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLite Best Practices](https://www.sqlite.org/bestpractice.html)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)

### Design Resources

- [Windows Design Principles](https://learn.microsoft.com/en-us/windows/apps/design/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

## 🎯 Next Steps

### Immediate Actions (This Week)

1. Set up development environment
2. Create project repository structure
3. Initialize SQLite database with schema
4. Build basic PyQt6 window with platform detection
5. Implement first CRUD operation (Item creation)

### Developer Onboarding

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Initialize database: `python scripts/init_db.py`
5. Run application: `python src/main.py`

---

**Document Status:** Living document - updated weekly during active development  
**Owner:** Senior Python Developer  
**Stakeholders:** Product Manager, Food Pantry Managers, Volunteer Coordinators
