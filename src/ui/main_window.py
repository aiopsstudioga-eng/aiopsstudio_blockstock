"""
Main window for AIOps Studio - Inventory.

Windows main application window with navigation.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont

from utils.platform_detect import (
    get_platform, get_font_family, 
    get_modifier_key, should_use_native_menubar
)
from services.inventory_service import InventoryService


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Initialize service
        self.service = InventoryService()
        
        # Set up UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("AIOps Studio - Inventory")
        self.setMinimumSize(1000, 700)
        
        # Set platform-appropriate font
        font = QFont(get_font_family(), 10)
        self.setFont(font)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar navigation
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)
        
        # Add pages
        self.add_pages()
        
        # Show dashboard by default
        self.content_stack.setCurrentIndex(0)
        
    def create_menu_bar(self):
        """Create menu bar with platform-specific behavior."""
        menubar = self.menuBar()
        
        # Set native menu bar (Always False for Windows)
        if should_use_native_menubar():
            menubar.setNativeMenuBar(True)
        else:
            menubar.setNativeMenuBar(False)
        
        modifier = get_modifier_key()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        backup_action = QAction("&Backup Database", self)
        backup_action.setShortcut(f"{modifier}+B")
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(f"{modifier}+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Inventory menu
        inventory_menu = menubar.addMenu("&Inventory")
        
        new_item_action = QAction("&New Item", self)
        new_item_action.setShortcut(f"{modifier}+N")
        new_item_action.triggered.connect(self.show_new_item)
        inventory_menu.addAction(new_item_action)
        
        purchase_action = QAction("&Purchase", self)
        purchase_action.setShortcut(f"{modifier}+P")
        purchase_action.triggered.connect(self.show_purchase)
        inventory_menu.addAction(purchase_action)
        
        donation_action = QAction("&Donation", self)
        donation_action.setShortcut(f"{modifier}+D")
        donation_action.triggered.connect(self.show_donation)
        inventory_menu.addAction(donation_action)
        
        distribute_action = QAction("D&istribute", self)
        distribute_action.setShortcut(f"{modifier}+I")
        distribute_action.triggered.connect(self.show_distribution)
        inventory_menu.addAction(distribute_action)
        
        # Reports menu
        reports_menu = menubar.addMenu("&Reports")
        
        financial_action = QAction("&Financial Report", self)
        financial_action.triggered.connect(self.show_financial_report)
        reports_menu.addAction(financial_action)
        
        impact_action = QAction("&Impact Report", self)
        impact_action.triggered.connect(self.show_impact_report)
        reports_menu.addAction(impact_action)
        
        stock_action = QAction("&Stock Status", self)
        stock_action.triggered.connect(self.show_stock_status)
        reports_menu.addAction(stock_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_sidebar(self) -> QWidget:
        """
        Create sidebar navigation.
        
        Returns:
            QWidget: Sidebar widget
        """
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(0)
        
        # App title
        title = QLabel("AIOps Studio")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Inventory")
        subtitle.setStyleSheet("font-size: 10pt; padding: 0px 20px 20px 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", 0),
            ("📦 Items", 1),
            ("📥 Intake", 2),
            ("📤 Distribution", 3),
            ("📈 Reports", 4),
        ]
        
        for text, index in nav_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, i=index: self.content_stack.setCurrentIndex(i))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Database info at bottom
        db_info = QLabel("Database: Connected")
        db_info.setStyleSheet("font-size: 9pt; padding: 20px; color: #95a5a6;")
        layout.addWidget(db_info)
        
        return sidebar
    
    def add_pages(self):
        """Add content pages to stack."""
        # Dashboard
        dashboard = self.create_dashboard_page()
        self.content_stack.addWidget(dashboard)
        
        # Items page (functional)
        from ui.items_page import ItemsPage
        items_page = ItemsPage(self.service)
        self.content_stack.addWidget(items_page)
        
        # Intake page
        intake_page = self.create_intake_page()
        self.content_stack.addWidget(intake_page)
        
        # Distribution page
        dist_page = self.create_distribution_page()
        self.content_stack.addWidget(dist_page)
        
        # Reports page (functional)
        from ui.reports_page import ReportsPage
        reports_page = ReportsPage(self.service.db_manager.db_path)
        self.content_stack.addWidget(reports_page)
    
    def create_intake_page(self) -> QWidget:
        """Create intake page with purchase and donation buttons."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Inventory Intake")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        desc = QLabel("Record purchases and donations")
        desc.setStyleSheet("font-size: 12pt; color: #7f8c8d; margin-bottom: 40px;")
        layout.addWidget(desc)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        
        # Purchase button
        purchase_btn = self.create_intake_card(
            "💰 Purchase",
            "Record purchased inventory\nUpdates weighted average cost",
            "#3498db",
            self.show_purchase
        )
        buttons_layout.addWidget(purchase_btn)
        
        # Donation button
        donation_btn = self.create_intake_card(
            "🎁 Donation",
            "Record donated inventory\nZero cost, tracks fair market value",
            "#27ae60",
            self.show_donation
        )
        buttons_layout.addWidget(donation_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        return page
    
    def create_distribution_page(self) -> QWidget:
        """Create distribution page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Distribution")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        desc = QLabel("Distribute items to clients or record spoilage/internal use")
        desc.setStyleSheet("font-size: 12pt; color: #7f8c8d; margin-bottom: 40px;")
        layout.addWidget(desc)
        
        # Distribution button
        dist_btn = self.create_intake_card(
            "📤 Record Distribution",
            "Distribute items with reason codes:\n• Client Distribution\n• Spoilage/Expiration\n• Internal Use",
            "#e67e22",
            self.show_distribution
        )
        
        button_container = QHBoxLayout()
        button_container.addWidget(dist_btn)
        button_container.addStretch()
        
        layout.addLayout(button_container)
        layout.addStretch()
        
        return page
    
    def create_intake_card(self, title: str, description: str, color: str, callback) -> QPushButton:
        """Create an intake action card button."""
        btn = QPushButton()
        btn.setFixedSize(300, 200)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 20px;
                font-size: 18pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        
        # Create layout for button content
        btn_layout = QVBoxLayout(btn)
        btn_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        btn_layout.addWidget(title_label)
        
        btn_layout.addSpacing(10)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11pt; font-weight: normal;")
        desc_label.setWordWrap(True)
        btn_layout.addWidget(desc_label)
        
        btn_layout.addStretch()
        
        return btn
    
    def darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 10%."""
        # Simple darkening - reduce each RGB component
        color_map = {
            "#3498db": "#2980b9",  # Blue
            "#27ae60": "#229954",  # Green
            "#e67e22": "#d35400",  # Orange
        }
        return color_map.get(hex_color, hex_color)

    
    def create_dashboard_page(self) -> QWidget:
        """Create dashboard page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Get statistics
        try:
            items = self.service.get_all_items()
            below_threshold = self.service.get_items_below_threshold()
            
            total_items = len(items)
            total_value = sum(item.total_inventory_value_dollars for item in items)
            low_stock_count = len(below_threshold)
            
            # Stats cards
            stats_layout = QHBoxLayout()
            
            stats_layout.addWidget(self.create_stat_card(
                "Total Items", str(total_items), "#3498db"
            ))
            stats_layout.addWidget(self.create_stat_card(
                "Total Value", f"${total_value:,.2f}", "#2ecc71"
            ))
            stats_layout.addWidget(self.create_stat_card(
                "Low Stock", str(low_stock_count), "#e74c3c" if low_stock_count > 0 else "#95a5a6"
            ))
            
            layout.addLayout(stats_layout)
            
        except Exception as e:
            error_label = QLabel(f"Error loading dashboard: {e}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
        
        layout.addStretch()
        
        return page
    
    def create_stat_card(self, title: str, value: str, color: str) -> QWidget:
        """Create a statistics card."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12pt; color: #7f8c8d;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28pt; font-weight: bold;")
        layout.addWidget(value_label)
        
        return card
    
    def create_placeholder_page(self, title: str, description: str) -> QWidget:
        """Create a placeholder page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12pt; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        coming_soon = QLabel("🚧 Coming soon...")
        coming_soon.setStyleSheet("font-size: 18pt; color: #95a5a6;")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)
        
        layout.addStretch()
        
        return page
    
    # Menu action handlers
    def backup_database(self):
        """Backup database."""
        try:
            backup_path = self.service.db_manager.backup()
            QMessageBox.information(
                self,
                "Backup Complete",
                f"Database backed up to:\n{backup_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Error backing up database:\n{e}"
            )
    
    def show_new_item(self):
        """Show new item dialog."""
        from ui.item_dialog import ItemDialog
        dialog = ItemDialog(self.service, parent=self)
        if dialog.exec():
            # Refresh items page if visible
            if self.content_stack.currentIndex() == 1:
                items_page = self.content_stack.widget(1)
                items_page.load_items()
    
    def show_purchase(self):
        """Show purchase dialog."""
        from ui.intake_dialogs import PurchaseDialog
        dialog = PurchaseDialog(self.service, parent=self)
        dialog.exec()
    
    def show_donation(self):
        """Show donation dialog."""
        from ui.intake_dialogs import DonationDialog
        dialog = DonationDialog(self.service, parent=self)
        dialog.exec()
    
    def show_distribution(self):
        """Show distribution dialog."""
        from ui.distribution_dialog import DistributionDialog
        dialog = DistributionDialog(self.service, parent=self)
        dialog.exec()

    
    def show_financial_report(self):
        """Show financial report page."""
        self.content_stack.setCurrentIndex(4)  # Reports page
    
    def show_impact_report(self):
        """Show impact report page."""
        self.content_stack.setCurrentIndex(4)  # Reports page
    
    def show_stock_status(self):
        """Show stock status report page."""
        self.content_stack.setCurrentIndex(4)  # Reports page
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AIOps Studio - Inventory",
            "<h2>AIOps Studio - Inventory</h2>"
            "<p>Version 0.1.0-alpha</p>"
            "<p>Professional inventory management for food pantries</p>"
            "<p>© 2026 AIOps Studio</p>"
        )
