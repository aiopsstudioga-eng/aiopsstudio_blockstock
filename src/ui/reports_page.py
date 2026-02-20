"""
Reports page for generating and viewing reports.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDateEdit, QMessageBox, QFileDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QDesktopServices
from datetime import date

from services.reporting_service import ReportingService
from services.pdf_generator import PDFReportGenerator
from services.excel_generator import ExcelReportGenerator
from ui.components.report_card import ReportCard


class ReportsPage(QWidget):
    """Reports page."""
    
    def __init__(self, db_path: str = "inventory.db", parent=None):
        """
        Initialize reports page.
        
        Args:
            db_path: Path to database
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.reporting_service = ReportingService(db_path)
        self.pdf_generator = PDFReportGenerator()
        self.excel_generator = ExcelReportGenerator()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        desc = QLabel("Financial, impact, and stock status reports")
        desc.setStyleSheet("font-size: 12pt; color: #7f8c8d; margin-bottom: 40px;")
        layout.addWidget(desc)
        
        # Date range selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        # Default to 2 months ago to capture more historical data
        self.start_date.setDate(QDate.currentDate().addMonths(-2))
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        # Default to tomorrow to include any future-dated transactions
        self.end_date.setDate(QDate.currentDate().addDays(1))
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        layout.addSpacing(30)
        
        # Report cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)  # Consistent gap between cards
        
        # Financial Report Card
        financial_card = ReportCard(
            title="Financial Report",
            description="Cost of Goods Distributed (COGS)\nPDF Export",
            icon="💰",
            color="#3498db",
            callback=self.generate_financial_report
        )
        grid_layout.addWidget(financial_card, 0, 0)
        
        # Impact Report Card
        impact_card = ReportCard(
            title="Impact Report",
            description="Donations & Fair Market Value\nExcel Export",
            icon="🎁",
            color="#27ae60",
            callback=self.generate_impact_report
        )
        grid_layout.addWidget(impact_card, 0, 1)
        
        # Stock Status Card
        stock_card = ReportCard(
            title="Stock Status",
            description="Low stock alerts & inventory levels\nPDF Export",
            icon="📊",
            color="#e67e22",
            callback=self.generate_stock_report
        )
        grid_layout.addWidget(stock_card, 0, 2)
        
        # Purchases Report Card
        purchases_card = ReportCard(
            title="Purchases Report",
            description="Purchase transactions\nExcel Export",
            icon="📦",
            color="#9b59b6",
            callback=self.generate_purchases_report
        )
        # Add 'Today' button
        purchases_card.add_extra_button("Today", self.generate_purchases_report_today)
        grid_layout.addWidget(purchases_card, 1, 0)
        
        # Suppliers Report Card
        suppliers_card = ReportCard(
            title="Suppliers Report",
            description="Supplier purchases & notes\nExcel Export",
            icon="🏢",
            color="#16a085",
            callback=self.generate_suppliers_report
        )
        grid_layout.addWidget(suppliers_card, 1, 1)
        
        # Push items to top-left
        grid_layout.setRowStretch(2, 1)
        grid_layout.setColumnStretch(3, 1)
        
        layout.addLayout(grid_layout)
        
        layout.addSpacing(30)
        
        # Transaction History Export
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Export Transaction History:"))
        
        export_btn = QPushButton("Export to Excel")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        export_btn.clicked.connect(self.export_transaction_history)
        export_layout.addWidget(export_btn)
        
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        layout.addStretch()

    def darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#e67e22": "#d35400",
            "#9b59b6": "#8e44ad",
            "#16a085": "#138d75",
        }
        return color_map.get(hex_color, hex_color)
    
    def get_date_range(self):
        """Get selected date range."""
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        return start, end
    
    def generate_financial_report(self):
        """Generate financial report PDF."""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get data
            data = self.reporting_service.get_financial_report_data(start_date, end_date)
            
            if data['distribution_count'] == 0:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No distributions found in the selected date range."
                )
                return
            
            # Generate PDF
            filepath = self.pdf_generator.generate_financial_report(data)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Financial report generated successfully!\n\n"
                f"Total COGS: ${data['total_cogs_dollars']:,.2f}\n"
                f"Distributions: {data['distribution_count']}\n\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def generate_impact_report(self):
        """Generate impact report Excel."""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get data
            data = self.reporting_service.get_impact_report_data(start_date, end_date)
            
            if data['donation_count'] == 0:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No donations found in the selected date range."
                )
                return
            
            # Generate Excel
            filepath = self.excel_generator.generate_impact_report(data)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Impact report generated successfully!\n\n"
                f"Total Donations (FMV): ${data['total_donations_fmv_dollars']:,.2f}\n"
                f"Value Distributed: ${data['total_distributed_value_dollars']:,.2f}\n"
                f"Donations: {data['donation_count']}\n\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def generate_stock_report(self):
        """Generate stock status report PDF."""
        try:
            # Get data
            data = self.reporting_service.get_stock_status_data()
            
            # Generate PDF
            filepath = self.pdf_generator.generate_stock_status_report(data)
            
            # Build alert message
            alert_msg = ""
            if data['zero_stock_count'] > 0:
                alert_msg += f"⚠️ {data['zero_stock_count']} items out of stock\n"
            if data['below_threshold_count'] > 0:
                alert_msg += f"⚠️ {data['below_threshold_count']} items below reorder threshold\n"
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Stock status report generated successfully!\n\n"
                f"Total Items: {data['total_items']}\n"
                f"Total Value: ${data['total_value_dollars']:,.2f}\n"
                f"{alert_msg}\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def export_transaction_history(self):
        """Export transaction history to Excel."""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get transactions
            transactions = self.reporting_service.get_transaction_history(
                start_date=start_date,
                end_date=end_date,
                limit=None  # No limit for export
            )
            
            if not transactions:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No transactions found in the selected date range."
                )
                return
            
            # Generate Excel
            filepath = self.excel_generator.generate_transaction_export(transactions)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Export Complete",
                f"Transaction history exported successfully!\n\n"
                f"Transactions: {len(transactions)}\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export transactions: {e}")
    
    def generate_purchases_report(self):
        """Generate purchases report Excel."""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get data
            data = self.reporting_service.get_purchases_report_data(start_date, end_date)
            
            if data['total_purchases'] == 0:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No purchases found in the selected date range."
                )
                return
            
            # Generate Excel
            filepath = self.excel_generator.generate_purchases_report(data)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Purchases report generated successfully!\n\n"
                f"Total Purchases: {data['total_purchases']}\n"
                f"Total Cost: ${data['total_cost_dollars']:,.2f}\n"
                f"Unique Suppliers: {data['unique_suppliers']}\n\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def generate_purchases_report_today(self):
        """Generate purchases report for today only."""
        try:
            today = date.today()
            
            # Get data for today
            data = self.reporting_service.get_purchases_report_data(today, today)
            
            if data['total_purchases'] == 0:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No purchases found for today."
                )
                return
            
            # Generate Excel
            filepath = self.excel_generator.generate_purchases_report(data)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Today's purchases report generated successfully!\n\n"
                f"Total Purchases: {data['total_purchases']}\n"
                f"Total Cost: ${data['total_cost_dollars']:,.2f}\n"
                f"Unique Suppliers: {data['unique_suppliers']}\n\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
    
    def generate_suppliers_report(self):
        """Generate suppliers report Excel."""
        try:
            # Get data
            data = self.reporting_service.get_suppliers_report_data()
            
            if data['total_suppliers'] == 0:
                QMessageBox.information(
                    self,
                    "No Data",
                    "No suppliers found. Make sure you have purchase transactions with supplier names."
                )
                return
            
            # Generate Excel
            filepath = self.excel_generator.generate_suppliers_report(data)
            
            # Ask to open
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Suppliers report generated successfully!\n\n"
                f"Total Suppliers: {data['total_suppliers']}\n"
                f"Total Purchases: {data['total_purchases']}\n"
                f"Total Cost: ${data['total_cost_dollars']:,.2f}\n\n"
                f"Saved to: {filepath}\n\n"
                f"Would you like to open the report?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
