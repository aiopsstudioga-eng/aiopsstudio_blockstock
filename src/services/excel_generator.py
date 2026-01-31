"""
Excel report generator using Pandas.

Generates Excel reports for impact and detailed data export.
"""

from datetime import date
from pathlib import Path
from typing import Dict
import pandas as pd


class ExcelReportGenerator:
    """Generate Excel reports."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize Excel generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_impact_report(self, data: Dict) -> str:
        """
        Generate impact report Excel file.
        
        Args:
            data: Impact report data from ReportingService
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"impact_report_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Donations Received (FMV)',
                    'Total Value Distributed to Clients',
                    'Number of Donations',
                    'Number of Client Distributions'
                ],
                'Value': [
                    f"${data['total_donations_fmv_dollars']:,.2f}",
                    f"${data['total_distributed_value_dollars']:,.2f}",
                    data['donation_count'],
                    data['distributions_count']
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Donations detail sheet
            if data['donations']:
                donations_data = []
                for donation in data['donations']:
                    donations_data.append({
                        'Date': donation['date'][:10],
                        'Item': donation['item_name'],
                        'SKU': donation['sku'],
                        'Quantity': donation['quantity'],
                        'Fair Market Value': donation['fmv_cents'] / 100.0,
                        'Donor': donation['donor'] or 'Anonymous'
                    })
                
                donations_df = pd.DataFrame(donations_data)
                donations_df.to_excel(writer, sheet_name='Donations', index=False)
                
                # Format currency columns
                workbook = writer.book
                worksheet = writer.sheets['Donations']
                
                # Set column widths
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 15
                worksheet.column_dimensions['D'].width = 12
                worksheet.column_dimensions['E'].width = 20
                worksheet.column_dimensions['F'].width = 25
        
        return str(filepath)
    
    def generate_transaction_export(self, transactions: list) -> str:
        """
        Generate transaction history Excel export.
        
        Args:
            transactions: List of transaction dicts
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"transaction_history_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Prepare data
        trans_data = []
        for trans in transactions:
            trans_data.append({
                'Date': trans['date'][:10],
                'Type': trans['type'],
                'Item': trans['item_name'],
                'SKU': trans['sku'],
                'Quantity': trans['quantity'],
                'Unit Cost': trans['unit_cost_cents'] / 100.0 if trans['unit_cost_cents'] else 0,
                'FMV': trans['fmv_cents'] / 100.0 if trans['fmv_cents'] else 0,
                'COGS': trans['cogs_cents'] / 100.0 if trans['cogs_cents'] else 0,
                'Reason': trans['reason'] or '',
                'Supplier': trans['supplier'] or '',
                'Donor': trans['donor'] or '',
                'Notes': trans['notes'] or ''
            })
        
        # Create DataFrame
        df = pd.DataFrame(trans_data)
        
        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Format
            worksheet = writer.sheets['Transactions']
            worksheet.column_dimensions['A'].width = 12
            worksheet.column_dimensions['B'].width = 15
            worksheet.column_dimensions['C'].width = 30
            worksheet.column_dimensions['D'].width = 15
            worksheet.column_dimensions['E'].width = 12
            worksheet.column_dimensions['F'].width = 12
            worksheet.column_dimensions['G'].width = 12
            worksheet.column_dimensions['H'].width = 12
            worksheet.column_dimensions['I'].width = 15
            worksheet.column_dimensions['J'].width = 20
            worksheet.column_dimensions['K'].width = 20
            worksheet.column_dimensions['L'].width = 30
        
        return str(filepath)
