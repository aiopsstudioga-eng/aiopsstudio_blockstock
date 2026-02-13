"""
Reports page for generating and viewing reports.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QDateEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QDesktopServices
from datetime import date

from services.reporting_service import ReportingService
from services.pdf_generator import PDFReportGenerator
from services.excel_generator import ExcelReportGenerator


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
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        layout.addSpacing(30)
        
        # Report cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # Financial Report Card
        financial_card = self.create_report_card(
            "💰 Financial Report",
            "Cost of Goods Distributed (COGS)\nPDF Export",
            "#3498db",
            self.generate_financial_report
        )
        cards_layout.addWidget(financial_card)
        
        # Impact Report Card
        impact_card = self.create_report_card(
            "🎁 Impact Report",
            "Donations & Fair Market Value\nExcel Export",
            "#27ae60",
            self.generate_impact_report
        )
        cards_layout.addWidget(impact_card)
        
        # Stock Status Card
        stock_card = self.create_report_card(
            "📊 Stock Status",
            "Low stock alerts & inventory levels\nPDF Export",
            "#e67e22",
            self.generate_stock_report
        )
        cards_layout.addWidget(stock_card)
        
        layout.addLayout(cards_layout)
        
        layout.addSpacing(20)
        
        # Second row of report cards
        cards_layout_2 = QHBoxLayout()
        cards_layout_2.setSpacing(20)
        
        # Purchases Report Card
        purchases_card = self.create_purchases_report_card()
        cards_layout_2.addWidget(purchases_card)
        
        # Suppliers Report Card
        suppliers_card = self.create_report_card(
            "🏢 Suppliers Report",
            "Supplier purchases \u0026 notes\nExcel Export",
            "#16a085",
            self.generate_suppliers_report
        )
        cards_layout_2.addWidget(suppliers_card)
        
        cards_layout_2.addStretch()
        
        layout.addLayout(cards_layout_2)
        
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
    
    def create_report_card(self, title: str, description: str, color: str, callback) -> QWidget:
        """Create a report card widget."""
        card = QWidget()
        card.setFixedSize(250, 200)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {color};")
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        card_layout.addSpacing(10)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 10pt; color: #7f8c8d;")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # Generate button
        gen_btn = QPushButton("Generate")
        gen_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        gen_btn.clicked.connect(callback)
        card_layout.addWidget(gen_btn)
        
        return card
    
    def create_purchases_report_card(self) -> QWidget:
        """Create purchases report card with dual buttons."""
        card = QWidget()
        card.setFixedSize(250, 200)
        color = "#9b59b6"
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 10px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("📦 Purchases Report")
        title_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {color};")
        title_label.setWordWrap(True)
        card_layout.addWidget(title_label)
        
        card_layout.addSpacing(10)
        
        # Description
        desc_label = QLabel("Purchase transactions\nExcel Export")
        desc_label.setStyleSheet("font-size: 10pt; color: #7f8c8d;")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
        # Generate button
        gen_btn = QPushButton("Generate")
        gen_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8e44ad;
            }}
        """)
        gen_btn.clicked.connect(self.generate_purchases_report)
        buttons_layout.addWidget(gen_btn)
        
        # Today button
        today_btn = QPushButton("Today")
        today_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8e44ad;
            }}
        """)
        today_btn.clicked.connect(self.generate_purchases_report_today)
        buttons_layout.addWidget(today_btn)
        
        card_layout.addLayout(buttons_layout)
        
        return card
    
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
