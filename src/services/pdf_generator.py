"""
PDF report generator using ReportLab.

Generates professional PDF reports for financial and stock status.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from utils.app_paths import get_reports_dir


class PDFReportGenerator:
    """Generate PDF reports."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory to save reports (defaults to AppData/reports)
        """
        if output_dir is None:
            output_dir = get_reports_dir()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )

        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.whitesmoke
        )

        self.table_cell_style_black = ParagraphStyle(
            'TableCellBlack',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.black
        )

        self.category_header_style = ParagraphStyle(
            'CategoryHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a5276'),
            spaceBefore=10,
            spaceAfter=4,
        )
    
    def generate_financial_report(self, data: Dict) -> str:
        """
        Generate financial report PDF.
        
        Args:
            data: Financial report data from ReportingService
            
        Returns:
            str: Path to generated PDF
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"financial_report_{today}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph("Financial Report - Cost of Goods Distributed", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # Date range
        start = data['start_date'].isoformat() if data['start_date'] else "Beginning"
        end = data['end_date'].isoformat() if data['end_date'] else "Present"
        date_range = Paragraph(f"<b>Period:</b> {start} to {end}", self.styles['Normal'])
        story.append(date_range)
        story.append(Spacer(1, 0.3 * inch))
        
        # Summary table
        summary_data = [
            ['Category', 'Amount'],
            ['Client Distributions', f"${data['client_cogs_dollars']:,.2f}"],
            ['Spoilage/Waste', f"${data['spoilage_cogs_dollars']:,.2f}"],
            ['Internal Use', f"${data['internal_cogs_dollars']:,.2f}"],
            ['', ''],
            ['Total COGS', f"${data['total_cogs_dollars']:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#3498db')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Detailed transactions
        if data['distributions']:
            heading = Paragraph("Detailed Transactions", self.heading_style)
            story.append(heading)
            
            # Transaction table header
            trans_data = [['Date', 'Item', 'Qty', 'Unit Cost', 'Total', 'Reason']]
            
            for dist in data['distributions']:
                item_text = f"{dist['item_name']} ({dist['sku']})"
                # Use Paragraph for wrapping
                item_para = Paragraph(item_text, self.table_cell_style_black)
                reason_para = Paragraph(dist['reason'], self.table_cell_style_black)

                trans_data.append([
                    dist['date'][:10],  # Date only
                    item_para,
                    f"{dist['quantity']:.1f}",
                    f"${dist['unit_cost_cents'] / 100:.2f}",
                    f"${dist['total_cogs_cents'] / 100:.2f}",
                    reason_para
                ])
            
            # Adjusted widths to fit 7.5" (8.5 - 0.5 - 0.5)
            # Old: [1, 2, 0.7, 1, 1, 1] = 6.7.   New target ~7.5
            trans_table = Table(trans_data, colWidths=[1*inch, 2.5*inch, 0.7*inch, 1*inch, 1*inch, 1.3*inch])
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Align top for wrapped text
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            story.append(trans_table)
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_stock_status_report(self, data: Dict) -> str:
        """
        Generate stock status report PDF.
        
        Args:
            data: Stock status data from ReportingService
            
        Returns:
            str: Path to generated PDF
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"stock_status_{today}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph("Stock Status Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # Summary
        summary_text = f"""
        <b>Total Items:</b> {data['total_items']}<br/>
        <b>Total Inventory Value:</b> ${data['total_value_dollars']:,.2f}<br/>
        <b>Items OK:</b> {data['ok_count']}<br/>
        <b>Items Below Threshold:</b> {data['below_threshold_count']}<br/>
        <b>Items Out of Stock:</b> {data['zero_stock_count']}
        """
        summary = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 0.3 * inch))
        
        # Inventory items grouped by category
        if data.get('items_by_category'):
            section_heading = Paragraph("Inventory by Category", self.heading_style)
            story.append(section_heading)
            story.append(Spacer(1, 0.1 * inch))

            # SKU: 1.2", Item: 2.2", Qty: 0.8", Threshold: 0.8", Status: 1.1", Value: 1.4" = 7.5"
            col_widths = [1.2*inch, 2.2*inch, 0.8*inch, 0.8*inch, 1.1*inch, 1.4*inch]

            for category_name, items in data['items_by_category'].items():
                # Category header
                story.append(Paragraph(category_name.upper(), self.category_header_style))

                table_rows = [['SKU', 'Item', 'Qty', 'Threshold', 'Status', 'Value']]

                for item in items:
                    name_para = Paragraph(item['name'], self.table_cell_style_black)
                    sku_para = Paragraph(item['sku'], self.table_cell_style_black)
                    value_dollars = item['value_cents'] / 100.0

                    if item['quantity'] == 0:
                        status = 'OUT OF STOCK'
                    elif item['quantity'] < item['threshold']:
                        status = 'LOW'
                    else:
                        status = 'OK'

                    table_rows.append([
                        sku_para,
                        name_para,
                        f"{item['quantity']:.1f}",
                        f"{item['threshold']}",
                        status,
                        f"${value_dollars:,.2f}",
                    ])

                cat_table = Table(table_rows, colWidths=col_widths)
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    # Highlight low/out-of-stock rows in the category table
                    *[
                        ('TEXTCOLOR', (4, i + 1), (4, i + 1),
                         colors.HexColor('#e74c3c') if table_rows[i + 1][4] in ('OUT OF STOCK', 'LOW') else colors.black)
                        for i in range(len(items))
                    ],
                ]))

                story.append(cat_table)
                story.append(Spacer(1, 0.25 * inch))
        
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
