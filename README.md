# AIOps Studio - Inventory

**Professional-grade inventory management system for food pantries**

## Overview

AIOps Studio - Inventory is a cross-platform desktop application designed specifically for non-profit food pantries. It solves the unique accounting challenge of tracking mixed "Zero-Cost" (donated) and "Purchased" goods using weighted average cost accounting.

## Key Features

- **Dual-Mode Inventory Intake**: Separate workflows for purchases and donations
- **Weighted Average Cost Accounting**: Accurate COGS calculation mixing $0 and purchased items
- **Cross-Platform**: Native look and feel on Windows and macOS
- **Professional Reporting**: PDF and Excel export for financial and impact reports
- **Audit Trail**: Immutable transaction history for compliance

## Technology Stack

- **Python 3.10+**
- **PyQt6** - Cross-platform GUI framework
- **SQLite 3** - Serverless database
- **ReportLab** - PDF generation
- **Pandas** - Excel export and data analysis

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AIOpsSoftware
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize database:
```bash
python scripts/init_db.py
```

5. Run the application:
```bash
python src/main.py
```

## Development

### Project Structure

```
AIOpsSoftware/
├── src/
│   ├── main.py                 # Application entry point
│   ├── models/                 # Data models
│   ├── services/               # Business logic
│   ├── ui/                     # PyQt6 UI components
│   ├── database/               # Database layer
│   └── utils/                  # Utilities
├── tests/                      # Test suite
├── scripts/                    # Utility scripts
├── resources/                  # Icons, styles
└── docs/                       # Documentation
```

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Building Executables

**Windows:**
```bash
pyinstaller build_windows.spec
```

**macOS:**
```bash
pyinstaller build_macos.spec
```

## Documentation

- [Roadmap](roadmap.md) - Development phases and milestones
- [Development Log](devlog.md) - Daily progress tracking
- [User Manual](docs/user_manual.md) - End-user documentation
- [PRD](Product%20Requirements%20Document%20(PRD).md) - Product requirements

## License

Open Source - TBD

## Support

For issues and questions, please open an issue on GitHub.

---

**Status:** Active Development - Phase 1 (MVP)  
**Version:** 0.1.0-alpha  
**Last Updated:** 2026-01-31
