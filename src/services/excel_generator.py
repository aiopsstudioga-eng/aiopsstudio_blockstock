"""
Excel report generator using Pandas.

Generates Excel reports for impact and detailed data export.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from utils.app_paths import get_reports_dir


class ExcelReportGenerator:
    """Generate Excel reports."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize Excel generator.
        
        Args:
            output_dir: Directory to save reports (defaults to AppData/reports)
        """
        if output_dir is None:
            output_dir = get_reports_dir()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    def generate_purchases_report(self, data: Dict) -> str:
        """
        Generate purchases report Excel file.
        
        Args:
            data: Purchases report data from ReportingService
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"purchases_report_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Purchases',
                    'Total Quantity',
                    'Total Cost',
                    'Unique Suppliers',
                    'Date Range'
                ],
                'Value': [
                    data['total_purchases'],
                    data['total_quantity'],
                    f"${data['total_cost_dollars']:,.2f}",
                    data['unique_suppliers'],
                    f"{data['start_date'] or 'All'} to {data['end_date'] or 'All'}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Purchases detail sheet
            if data['purchases']:
                purchases_data = []
                for purchase in data['purchases']:
                    purchases_data.append({
                        'Date': purchase['date'][:10],
                        'Item': purchase['item_name'],
                        'SKU': purchase['sku'],
                        'Category': purchase['category'],
                        'Quantity': purchase['quantity'],
                        'Unit Cost': purchase['unit_cost_cents'] / 100.0,
                        'Total Cost': purchase['total_cost_cents'] / 100.0,
                        'Supplier': purchase['supplier'] or '',
                        'Notes': purchase['notes'] or ''
                    })
                
                purchases_df = pd.DataFrame(purchases_data)
                purchases_df.to_excel(writer, sheet_name='Purchases', index=False)
                
                # Format columns
                worksheet = writer.sheets['Purchases']
                worksheet.column_dimensions['A'].width = 12
                worksheet.column_dimensions['B'].width = 30
                worksheet.column_dimensions['C'].width = 15
                worksheet.column_dimensions['D'].width = 20
                worksheet.column_dimensions['E'].width = 12
                worksheet.column_dimensions['F'].width = 12
                worksheet.column_dimensions['G'].width = 12
                worksheet.column_dimensions['H'].width = 25
                worksheet.column_dimensions['I'].width = 40
        
        return str(filepath)
    
    def generate_suppliers_report(self, data: Dict) -> str:
        """
        Generate suppliers report Excel file.
        
        Args:
            data: Suppliers report data from ReportingService
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"suppliers_report_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Suppliers',
                    'Total Purchases',
                    'Total Cost'
                ],
                'Value': [
                    data['total_suppliers'],
                    data['total_purchases'],
                    f"${data['total_cost_dollars']:,.2f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Suppliers detail sheet
            if data['suppliers']:
                suppliers_data = []
                for supplier in data['suppliers']:
                    suppliers_data.append({
                        'Supplier': supplier['supplier'],
                        'Purchase Count': supplier['purchase_count'],
                        'Total Quantity': supplier['total_quantity'],
                        'Total Cost': supplier['total_cost_dollars'],
                        'First Purchase': supplier['first_purchase'][:10] if supplier['first_purchase'] else '',
                        'Last Purchase': supplier['last_purchase'][:10] if supplier['last_purchase'] else '',
                        'Notes': supplier['notes']
                    })
                
                suppliers_df = pd.DataFrame(suppliers_data)
                suppliers_df.to_excel(writer, sheet_name='Suppliers', index=False)
                
                # Format columns
                worksheet = writer.sheets['Suppliers']
                worksheet.column_dimensions['A'].width = 25
                worksheet.column_dimensions['B'].width = 15
                worksheet.column_dimensions['C'].width = 15
                worksheet.column_dimensions['D'].width = 15
                worksheet.column_dimensions['E'].width = 15
                worksheet.column_dimensions['F'].width = 15
                worksheet.column_dimensions['G'].width = 50
        
        return str(filepath)
