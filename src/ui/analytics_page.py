"""
Analytics page for advanced inventory analytics and forecasting.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QGridLayout, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

from services.analytics_service import AnalyticsService


class AnalyticsPage(QWidget):
    """Analytics and forecasting page."""
    
    def __init__(self, db_path: str = "inventory.db", parent=None):
        """
        Initialize analytics page.
        
        Args:
            db_path: Path to database
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.analytics_service = AnalyticsService(db_path)
        self.current_forecast_days = 30
        self.current_lookback_days = 90
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Advanced Analytics")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        desc = QLabel("Predictive forecasting, seasonal trends, and donor impact analysis")
        desc.setStyleSheet("font-size: 12pt; color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(desc)
        
        # Tab buttons for different analytics sections
        self.create_tab_buttons(layout)
        
        # Stack widget for different views
        from PyQt6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Create individual pages
        self.create_forecast_page()
        self.create_trends_page()
        self.create_donor_page()
        
        # Start on forecast page
        self.stack.setCurrentIndex(0)
    
    def create_tab_buttons(self, parent_layout):
        """Create tab navigation buttons."""
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(10)
        
        # Forecast button
        self.forecast_btn = QPushButton("📈 Inventory Forecast")
        self.forecast_btn.setFixedHeight(45)
        self.forecast_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #1a5276;
            }
        """)
        self.forecast_btn.clicked.connect(lambda: self.switch_tab(0))
        tab_layout.addWidget(self.forecast_btn)
        
        # Trends button
        self.trends_btn = QPushButton("📊 Seasonal Trends")
        self.trends_btn.setFixedHeight(45)
        self.trends_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1a252f;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #34495e;
            }
        """)
        self.trends_btn.clicked.connect(lambda: self.switch_tab(1))
        tab_layout.addWidget(self.trends_btn)
        
        # Donor button
        self.donor_btn = QPushButton("❤️ Donor Impact")
        self.donor_btn.setFixedHeight(45)
        self.donor_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #145a32;
            }
        """)
        self.donor_btn.clicked.connect(lambda: self.switch_tab(2))
        tab_layout.addWidget(self.donor_btn)
        
        tab_layout.addStretch()
        parent_layout.addLayout(tab_layout)
        
        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #ecf0f1; height: 2px; margin-bottom: 20px;")
        separator.setFixedHeight(2)
        parent_layout.addWidget(separator)
    
    def switch_tab(self, index: int):
        """Switch between analytics tabs."""
        self.stack.setCurrentIndex(index)
        
        # Update button styles
        buttons = [self.forecast_btn, self.trends_btn, self.donor_btn]
        colors = ['#3498db', '#2c3e50', '#27ae60']
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors[i]};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 12pt;
                        font-weight: bold;
                        padding: 10px 20px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colors[i]};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 12pt;
                        font-weight: bold;
                        padding: 10px 20px;
                        opacity: 0.7;
                    }}
                    QPushButton:hover {{
                        opacity: 1;
                    }}
                """)
    
    def create_forecast_page(self):
        """Create inventory forecast page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls = QHBoxLayout()
        
        # Days ahead selector
        controls.addWidget(QLabel("Forecast Period:"))
        self.forecast_days = QSpinBox()
        self.forecast_days.setMinimum(7)
        self.forecast_days.setMaximum(180)
        self.forecast_days.setValue(30)
        self.forecast_days.setSuffix(" days")
        self.forecast_days.valueChanged.connect(self.on_forecast_settings_changed)
        controls.addWidget(self.forecast_days)
        
        controls.addSpacing(20)
        
        # Lookback period selector
        controls.addWidget(QLabel("Analyze History:"))
        self.lookback_days = QComboBox()
        self.lookback_days.addItems(["30 days", "60 days", "90 days", "180 days"])
        self.lookback_days.setCurrentIndex(2)  # 90 days default
        self.lookback_days.currentTextChanged.connect(self.on_forecast_settings_changed)
        controls.addWidget(self.lookback_days)
        
        controls.addStretch()
        
        # Generate button
        generate_btn = QPushButton("🔄 Generate Forecast")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_btn.clicked.connect(self.generate_forecast)
        controls.addWidget(generate_btn)
        
        layout.addLayout(controls)
        
        layout.addSpacing(20)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        # Critical items card
        self.critical_card = self.create_summary_card("🔴 Critical Risk", "0 items", "#e74c3c")
        summary_layout.addWidget(self.critical_card)
        
        # High risk card
        self.high_risk_card = self.create_summary_card("🟠 High Risk", "0 items", "#e67e22")
        summary_layout.addWidget(self.high_risk_card)
        
        # Medium risk card
        self.medium_risk_card = self.create_summary_card("🟡 Medium Risk", "0 items", "#f1c40f")
        summary_layout.addWidget(self.medium_risk_card)
        
        # Low risk card
        self.low_risk_card = self.create_summary_card("🟢 Low Risk", "0 items", "#27ae60")
        summary_layout.addWidget(self.low_risk_card)
        
        layout.addLayout(summary_layout)
        
        layout.addSpacing(20)
        
        # Forecast table
        self.forecast_table = QTableWidget()
        self.forecast_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.forecast_table.setAlternatingRowColors(True)
        self.forecast_table.setColumnCount(9)
        self.forecast_table.setHorizontalHeaderLabels([
            "SKU", "Item Name", "Current Qty", "Daily Rate", 
            "Projected Qty", "Days Until Stockout", "Risk Level", "Confidence", "Days Ahead"
        ])
        header = self.forecast_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(9):
            if i != 1:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.forecast_table)
        
        self.stack.addWidget(page)
    
    def create_trends_page(self):
        """Create seasonal trends page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls = QHBoxLayout()
        
        # Year selector
        controls.addWidget(QLabel("Year:"))
        self.trend_year = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 1):
            self.trend_year.addItem(str(year))
        self.trend_year.setCurrentText(str(current_year))
        controls.addWidget(self.trend_year)
        
        controls.addStretch()
        
        # Generate button
        generate_btn = QPushButton("🔄 Generate Trends")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a252f;
            }
        """)
        generate_btn.clicked.connect(self.generate_trends)
        controls.addWidget(generate_btn)
        
        layout.addLayout(controls)
        
        layout.addSpacing(20)
        
        # Summary
        self.trends_summary = QLabel()
        self.trends_summary.setStyleSheet("font-size: 12pt; padding: 10px; background-color: #ecf0f1; border-radius: 4px;")
        layout.addWidget(self.trends_summary)
        
        layout.addSpacing(20)
        
        # Monthly trends table
        self.trends_table = QTableWidget()
        self.trends_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.trends_table.setAlternatingRowColors(True)
        self.trends_table.setColumnCount(7)
        self.trends_table.setHorizontalHeaderLabels([
            "Month", "Distributions (Qty)", "Distributions ($)", 
            "Donations (Qty)", "Donations ($)", "Purchases (Qty)", "Purchases ($)"
        ])
        trends_header = self.trends_table.horizontalHeader()
        trends_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, 7):
            trends_header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.trends_table)
        
        # YoY comparison section
        yoy_label = QLabel("Year-over-Year Comparison")
        yoy_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-top: 20px;")
        layout.addWidget(yoy_label)
        
        self.yoy_table = QTableWidget()
        self.yoy_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.yoy_table.setAlternatingRowColors(True)
        self.yoy_table.setColumnCount(4)
        self.yoy_table.setHorizontalHeaderLabels([
            "Year", "Total Distributions", "Total Donations", "YoY Change"
        ])
        
        layout.addWidget(self.yoy_table)
        
        self.stack.addWidget(page)
    
    def create_donor_page(self):
        """Create donor impact page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls = QHBoxLayout()
        
        controls.addStretch()
        
        # Generate button
        generate_btn = QPushButton("🔄 Generate Donor Report")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        generate_btn.clicked.connect(self.generate_donor_report)
        controls.addWidget(generate_btn)
        
        layout.addLayout(controls)
        
        layout.addSpacing(20)
        
        # Summary cards
        donor_summary = QHBoxLayout()
        donor_summary.setSpacing(20)
        
        # Total donors card
        self.total_donors_card = self.create_summary_card("👥 Total Donors", "0", "#3498db")
        donor_summary.addWidget(self.total_donors_card)
        
        # Total donations card
        self.total_donations_card = self.create_summary_card("🎁 Total Donations", "0", "#27ae60")
        donor_summary.addWidget(self.total_donations_card)
        
        # Total FMV card
        self.total_fmv_card = self.create_summary_card("💰 Total FMV", "$0", "#9b59b6")
        donor_summary.addWidget(self.total_fmv_card)
        
        layout.addLayout(donor_summary)
        
        layout.addSpacing(20)
        
        # Donor table
        self.donor_table = QTableWidget()
        self.donor_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.donor_table.setAlternatingRowColors(True)
        self.donor_table.setColumnCount(5)
        self.donor_table.setHorizontalHeaderLabels([
            "Donor Name", "Donation Count", "Total Quantity", "Total FMV ($)", "% of Total"
        ])
        donor_header = self.donor_table.horizontalHeader()
        donor_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            donor_header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.donor_table)
        
        self.stack.addWidget(page)
    
    def create_summary_card(self, title: str, value: str, color: str) -> QWidget:
        """Create a summary card widget."""
        card = QWidget()
        card.setMinimumWidth(180)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 11pt; color: {color}; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2c3e50;")
        layout.addWidget(value_label)
        
        return card
    
    def update_summary_card(self, card: QWidget, value: str):
        """Update the value in a summary card."""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def on_forecast_settings_changed(self):
        """Handle forecast settings changes."""
        self.current_forecast_days = self.forecast_days.value()
        lookback_text = self.lookback_days.currentText()
        self.current_lookback_days = int(lookback_text.split()[0])
    
    def generate_forecast(self):
        """Generate inventory forecast."""
        try:
            days_ahead = self.forecast_days.value()
            lookback_text = self.lookback_days.currentText()
            lookback_days = int(lookback_text.split()[0])
            
            forecasts = self.analytics_service.get_inventory_forecast(
                days_ahead=days_ahead,
                lookback_days=lookback_days
            )
            
            # Update table
            self.forecast_table.setRowCount(len(forecasts))
            
            # Count by risk level
            critical_count = 0
            high_count = 0
            medium_count = 0
            low_count = 0
            
            for row, data in enumerate(forecasts):
                risk = data['risk_level']
                if risk == 'critical':
                    critical_count += 1
                elif risk == 'high':
                    high_count += 1
                elif risk == 'medium':
                    medium_count += 1
                else:
                    low_count += 1
                
                # Color by risk
                if risk == 'critical':
                    bg_color = "#ffebee"
                elif risk == 'high':
                    bg_color = "#fff3e0"
                elif risk == 'medium':
                    bg_color = "#fffde7"
                else:
                    bg_color = "white"
                
                items = [
                    data['sku'],
                    data['name'],
                    str(data['current_quantity']),
                    str(data['daily_consumption_rate']),
                    str(data['projected_quantity']),
                    str(data['days_until_stockout']) if data['days_until_stockout'] else "N/A",
                    data['risk_level'].upper(),
                    data['confidence'].upper(),
                    str(data['days_ahead'])
                ]
                
                for col, item in enumerate(items):
                    cell = QTableWidgetItem(item)
                    cell.setBackground(QColor(bg_color))
                    if col == 6:  # Risk level column
                        if risk == 'critical':
                            cell.setForeground(QColor("#c0392b"))
                        elif risk == 'high':
                            cell.setForeground(QColor("#d35400"))
                        elif risk == 'medium':
                            cell.setForeground(QColor("#f39c12"))
                        else:
                            cell.setForeground(QColor("#27ae60"))
                        font = QFont()
                        font.setBold(True)
                        cell.setFont(font)
                    self.forecast_table.setItem(row, col, cell)
            
            # Update summary cards
            self.update_summary_card(self.critical_card, f"{critical_count} items")
            self.update_summary_card(self.high_risk_card, f"{high_count} items")
            self.update_summary_card(self.medium_risk_card, f"{medium_count} items")
            self.update_summary_card(self.low_risk_card, f"{low_count} items")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate forecast: {e}")
    
    def generate_trends(self):
        """Generate seasonal trends."""
        try:
            year = int(self.trend_year.currentText())
            
            # Get seasonal trends
            trends = self.analytics_service.get_seasonal_trends(year=year)
            
            # Update summary
            totals = trends['totals']
            summary_text = (
                f"<b>{year} Summary:</b> "
                f"Distributions: {int(totals['distributions_qty'])} units (${totals['distributions_value']:,.2f}) | "
                f"Donations: {int(totals['donations_qty'])} units (${totals['donations_value']:,.2f}) | "
                f"Purchases: {int(totals['purchases_qty'])} units (${totals['purchases_value']:,.2f}) | "
                f"<b>Peak Month: {trends['peak_month']}</b>"
            )
            self.trends_summary.setText(summary_text)
            
            # Update monthly table
            months = trends['months']
            self.trends_table.setRowCount(len(months))
            
            for row, month in enumerate(months):
                items = [
                    month['month_name'],
                    str(int(month['distributions_qty'])),
                    f"${month['distributions_value']:,.2f}",
                    str(int(month['donations_qty'])),
                    f"${month['donations_value']:,.2f}",
                    str(int(month['purchases_qty'])),
                    f"${month['purchases_value']:,.2f}"
                ]
                
                for col, item in enumerate(items):
                    cell = QTableWidgetItem(item)
                    self.trends_table.setItem(row, col, cell)
            
            # Get YoY comparison
            yoy = self.analytics_service.get_year_over_year_comparison()
            
            self.yoy_table.setRowCount(len(yoy['years']))
            for row, year in enumerate(yoy['years']):
                data = yoy['data'][year]
                change = yoy['yoy_changes'][year]
                
                items = [
                    str(year),
                    str(int(data['distributions_qty'])),
                    str(int(data['donations_qty'])),
                    f"{change:+.1f}%" if change is not None else "N/A"
                ]
                
                for col, item in enumerate(items):
                    cell = QTableWidgetItem(item)
                    if col == 3 and change is not None:
                        if change > 0:
                            cell.setForeground(QColor("#27ae60"))
                        elif change < 0:
                            cell.setForeground(QColor("#e74c3c"))
                    self.yoy_table.setItem(row, col, cell)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate trends: {e}")
    
    def generate_donor_report(self):
        """Generate donor impact report."""
        try:
            summary = self.analytics_service.get_donor_impact_summary()
            
            # Update summary cards
            self.update_summary_card(self.total_donors_card, str(summary['total_donors']))
            self.update_summary_card(self.total_donations_card, str(summary['total_donations']))
            self.update_summary_card(self.total_fmv_card, f"${summary['total_fmv_dollars']:,.2f}")
            
            # Update table
            donors = summary['donors']
            self.donor_table.setRowCount(len(donors))
            
            total_fmv = summary['total_fmv_cents']
            
            for row, donor in enumerate(donors):
                pct = (donor['total_fmv_cents'] / total_fmv * 100) if total_fmv > 0 else 0
                
                items = [
                    donor['donor'],
                    str(donor['donation_count']),
                    str(int(donor['total_quantity'])),
                    f"${donor['total_fmv_dollars']:,.2f}",
                    f"{pct:.1f}%"
                ]
                
                for col, item in enumerate(items):
                    cell = QTableWidgetItem(item)
                    if col == 0:
                        font = QFont()
                        font.setBold(True)
                        cell.setFont(font)
                    self.donor_table.setItem(row, col, cell)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate donor report: {e}")
