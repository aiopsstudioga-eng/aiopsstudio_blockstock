"""
Dashboard page for identifying key inventory metrics at a glance.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from services.reporting_service import ReportingService


class StatCard(QFrame):
    """
    A card displaying a single statistic.
    """
    def __init__(self, title: str, value: str, color: str = "#3498db", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
            }}
        """)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; font-weight: bold;")
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {color}; font-size: 24pt; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)


class DashboardPage(QWidget):
    """Dashboard page with charts and stats."""
    
    def __init__(self, service: ReportingService, parent=None):
        super().__init__(parent)
        self.service = service
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)
        
        # KPI Cards (Top Row)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        self.total_value_card = StatCard("Total Inventory Value", "$0.00", "#2ecc71")
        self.low_stock_card = StatCard("Low Stock Items", "0", "#e74c3c")
        self.total_items_card = StatCard("Total Active Items", "0", "#3498db")
        
        kpi_layout.addWidget(self.total_value_card)
        kpi_layout.addWidget(self.low_stock_card)
        kpi_layout.addWidget(self.total_items_card)
        
        layout.addLayout(kpi_layout)
        
        # Charts (Bottom Row)
        charts_layout = QHBoxLayout()
        
        # Value by Category Chart
        self.category_figure = Figure(figsize=(5, 4), dpi=100)
        self.category_canvas = FigureCanvasQTAgg(self.category_figure)
        charts_layout.addWidget(self.category_canvas)
        
        # Top Distributed Items Chart
        self.distributed_figure = Figure(figsize=(5, 4), dpi=100)
        self.distributed_canvas = FigureCanvasQTAgg(self.distributed_figure)
        charts_layout.addWidget(self.distributed_canvas)
        
        layout.addLayout(charts_layout)
        
    def load_data(self):
        """Load and display dashboard data."""
        try:
            stats = self.service.get_dashboard_stats()
            
            # Update KPI Cards
            self.total_value_card.value_label.setText(f"${stats['total_inventory_value_dollars']:,.2f}")
            self.low_stock_card.value_label.setText(str(stats['low_stock_count']))
            self.total_items_card.value_label.setText(str(stats['total_items_count']))
            
            # --- Update Category Chart (Pie) ---
            self.category_figure.clear()
            ax1 = self.category_figure.add_subplot(111)
            
            categories = stats['value_by_category']
            if categories:
                labels = [c['category'] for c in categories]
                values = [c['value_dollars'] for c in categories]
                
                # Pie chart with labels outside and connecting lines
                colors = plt.cm.Set3.colors
                
                # Small explode for visual separation
                explode = [0.05] * len(values)
                
                wedges, texts, autotexts = ax1.pie(
                    values, 
                    labels=labels,
                    autopct='%1.1f%%',
                    startangle=90, 
                    colors=colors,
                    explode=explode,
                    pctdistance=0.85,  # Percentage inside
                    labeldistance=1.1,  # Labels outside
                    textprops={'fontsize': 9},
                    autopct_kw={'fontsize': 9, 'weight': 'bold'}
                )
                
                # Style the percentage labels
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_weight('bold')
                
                ax1.set_title("Inventory Value by Category", fontsize=11, weight='bold', pad=20)
            else:
                ax1.text(0.5, 0.5, "No Data", ha='center', va='center')
                
            self.category_canvas.draw()
            
            # --- Update Distribution Chart (Bar) ---
            self.distributed_figure.clear()
            ax2 = self.distributed_figure.add_subplot(111)
            
            items = stats['top_distributed_items']
            if items:
                names = [i['name'] for i in items]
                quantities = [i['quantity'] for i in items]
                
                # Vertical Bar chart
                bars = ax2.bar(names, quantities, color='#3498db')
                
                # Add counts on top of bars
                ax2.bar_label(bars)
                
                ax2.set_title("Top 5 Distributed Items (All Time)")
                ax2.set_ylabel("Units Distributed")
                # Rotate labels if they are long
                plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                self.distributed_figure.subplots_adjust(bottom=0.2) # Make room for labels
            else:
                ax2.text(0.5, 0.5, "No Data", ha='center', va='center')
                
            self.distributed_canvas.draw()
            
        except Exception as e:
            print(f"Error loading dashboard: {e}")
