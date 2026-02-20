"""
Dashboard page for identifying key inventory metrics at a glance.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from PyQt6.QtGui import QColor, QFont

# Matplotlib imports moved to local scope for faster startup
# import matplotlib
# matplotlib.use('QtAgg')
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt

from services.reporting_service import ReportingService
from utils.error_handler import show_error
from utils.logger import setup_logger

logger = setup_logger(__name__)



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
        
        layout.addLayout(kpi_layout)
        
        # Charts (Bottom Row)
        self.charts_layout = QHBoxLayout()
        self._init_charts() # Lazy load charts
        layout.addLayout(self.charts_layout)
        
    def _init_charts(self):
        """Initialize charts with local imports."""
        # Local import for performance
        import matplotlib
        matplotlib.use('QtAgg')
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        
        # Store classes for later use in load_data
        self.FigureCanvasQTAgg = FigureCanvasQTAgg
        self.Figure = Figure
        
        # Value by Category Chart
        self.category_figure = Figure(figsize=(5, 4), dpi=100)
        self.category_canvas = FigureCanvasQTAgg(self.category_figure)
        self.charts_layout.addWidget(self.category_canvas)
        
        # Top Distributed Items Chart
        self.distributed_figure = Figure(figsize=(5, 4), dpi=100)
        self.distributed_canvas = FigureCanvasQTAgg(self.distributed_figure)
        self.charts_layout.addWidget(self.distributed_canvas)
        
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
                
            if categories:
                labels = [c['category'] for c in categories]
                values = [c['value_dollars'] for c in categories]
                
                # Pie chart with labels outside and connecting lines
                # Import colormap locally
                import matplotlib.pyplot as plt
                colors = plt.cm.Set3.colors
                
                # Small explode for visual separation
                explode = [0.05] * len(values)
                
                # Define a function to hide small percentages
                def autopct_format(pct):
                    return ('%1.1f%%' % pct) if pct >= 5 else ''

                wedges, texts, autotexts = ax1.pie(
                    values, 
                    labels=None, # Hide external labels to prevent smashing
                    autopct=autopct_format,
                    startangle=90, 
                    colors=colors,
                    explode=explode,
                    pctdistance=0.85,
                    textprops={'fontsize': 9}
                )
                
                # Style the percentage labels
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_weight('bold')
                
                # Add Legend
                ax1.legend(
                    wedges, labels,
                    title="Categories",
                    loc="center left",
                    bbox_to_anchor=(0.9, 0, 0.5, 1),
                    fontsize='small'
                )
                
                ax1.set_title("Inventory Value by Category", fontsize=10, weight='bold')
                # Adjust margins to accommodate legend on the right
                self.category_figure.subplots_adjust(left=0.05, right=0.7, top=0.9, bottom=0.1)
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
                
                # Truncate long names for display
                display_names = []
                for name in names:
                    if len(name) > 20:
                        display_names.append(name[:17] + "...")
                    else:
                        display_names.append(name)

                # Vertical Bar chart
                bars = ax2.bar(display_names, quantities, color='#3498db')
                
                # Add counts on top of bars
                ax2.bar_label(bars, padding=3)
                
                ax2.set_title("Top 5 Distributed Items", pad=20)
                ax2.set_ylabel("Units")
                
                # Dynamic Y-limit to fit labels
                if quantities:
                    ax2.set_ylim(0, max(quantities) * 1.2)
                
                # Rotate labels if they are long
                # Import pyplot locally for setp
                import matplotlib.pyplot as plt
                plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                # Increase bottom margin for rotated labels
                self.distributed_figure.subplots_adjust(bottom=0.35, top=0.85)
            else:
                ax2.text(0.5, 0.5, "No Data", ha='center', va='center')
                
            self.distributed_canvas.draw()
            
        except Exception as e:
            show_error(
                self,
                "Dashboard Error",
                "Failed to load dashboard data. Please check the application logs for details.",
                exception=e
            )

