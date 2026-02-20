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

    def generate_inventory_forecast_report(self, data: list) -> str:
        """
        Generate inventory forecast report Excel file.
        
        Args:
            data: List of forecast dictionaries from AnalyticsService
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"inventory_forecast_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Prepare data for DataFrame
        forecast_data = []
        for item in data:
            forecast_data.append({
                'SKU': item['sku'],
                'Item Name': item['name'],  # Changed from 'name' based on typical service output, will verify
                'Current Qty': item['current_quantity'],
                'Daily Usage': item['daily_consumption_rate'],
                'Projected (30d)': item['projected_quantity'],
                'Days Until Stockout': item['days_until_stockout'] if item['days_until_stockout'] else 'N/A',
                'Risk Level': item['risk_level'].upper(),
                'Confidence': item['confidence'].upper()
            })
            
        # Create DataFrame
        df = pd.DataFrame(forecast_data)
        
        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Forecast', index=False)
            
            # Format
            workbook = writer.book
            worksheet = writer.sheets['Forecast']
            
            # Column widths
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 12
            worksheet.column_dimensions['D'].width = 12
            worksheet.column_dimensions['E'].width = 15
            worksheet.column_dimensions['F'].width = 18
            worksheet.column_dimensions['G'].width = 12
            worksheet.column_dimensions['H'].width = 12
            
            # Conditional formatting for Risk Level (simulated with manual iteration since openpyxl conditional formatting requires rule objects)
            # For simplicity in this implementation, we'll just rely on the text values
            
        return str(filepath)

    def generate_seasonal_trends_report(self, data: Dict) -> str:
        """
        Generate seasonal trends report Excel file.
        
        Args:
            data: Trends dictionary from AnalyticsService (contains 'months', 'totals', etc.)
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        year = data.get('year', date.today().year)
        filename = f"seasonal_trends_{year}.xlsx"
        filepath = self.output_dir / filename
        
        # Prepare Monthly Data
        monthly_data = []
        for month in data['months']:
            monthly_data.append({
                'Month': month['month_name'],
                'Distributions (Qty)': month['distributions_qty'],
                'Distributions ($)': month['distributions_value'],
                'Donations (Qty)': month['donations_qty'],
                'Donations ($)': month['donations_value'],
                'Purchases (Qty)': month['purchases_qty'],
                'Purchases ($)': month['purchases_value']
            })
        
        df_monthly = pd.DataFrame(monthly_data)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Monthly Data Sheet
            df_monthly.to_excel(writer, sheet_name='Monthly Trends', index=False)
            
            # Summary Sheet
            totals = data['totals']
            summary_data = {
                'Metric': [
                    'Total Distributions',
                    'Total Donations',
                    'Total Purchases',
                    'Peak Month',
                    'Peak Distribution Qty'
                ],
                'Value': [
                    f"{int(totals['distributions_qty'])} units (${totals['distributions_value']:,.2f})",
                    f"{int(totals['donations_qty'])} units (${totals['donations_value']:,.2f})",
                    f"{int(totals['purchases_qty'])} units (${totals['purchases_value']:,.2f})",
                    data['peak_month'],
                    int(data['peak_distribution_qty'])
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Check for YoY data if included in a wrapper or separate call - usually handled by separate report or combined data
            # For this exact method signature, we stick to the 'data' structure provided
            
            # Format Monthly Sheet
            ws_monthly = writer.sheets['Monthly Trends']
            ws_monthly.column_dimensions['A'].width = 10
            for col in ['B', 'C', 'D', 'E', 'F', 'G']:
                ws_monthly.column_dimensions[col].width = 18
                
            # Format Summary Sheet
            ws_summary = writer.sheets['Summary']
            ws_summary.column_dimensions['A'].width = 25
            ws_summary.column_dimensions['B'].width = 40
            
        return str(filepath)

    def generate_donor_impact_report(self, data: Dict) -> str:
        """
        Generate donor impact report Excel file.
        
        Args:
            data: Donor summary dictionary from AnalyticsService
            
        Returns:
            str: Path to generated Excel file
        """
        # Generate filename
        today = date.today().isoformat()
        filename = f"donor_impact_{today}.xlsx"
        filepath = self.output_dir / filename
        
        # Prepare Donor List
        donors_data = []
        total_fmv = data['total_fmv_cents']
        
        for donor in data['donors']:
            pct = (donor['total_fmv_cents'] / total_fmv * 100) if total_fmv > 0 else 0
            donors_data.append({
                'Donor Name': donor['donor'],
                'Donation Count': donor['donation_count'],
                'Total Quantity': int(donor['total_quantity']),
                'Total FMV ($)': donor['total_fmv_dollars'],
                '% of Total': f"{pct:.1f}%"
            })
            
        df_donors = pd.DataFrame(donors_data)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Donor Details Sheet
            df_donors.to_excel(writer, sheet_name='Donor Details', index=False)
            
            # Summary Sheet
            summary_data = {
                'Metric': [
                    'Total Donors',
                    'Total Donations Count',
                    'Total Items Donated',
                    'Total Fair Market Value'
                ],
                'Value': [
                    data['total_donors'],
                    data['total_donations'],
                    data['total_quantity'],
                    f"${data['total_fmv_dollars']:,.2f}"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Format Details Sheet
            ws_details = writer.sheets['Donor Details']
            ws_details.column_dimensions['A'].width = 30
            ws_details.column_dimensions['B'].width = 15
            ws_details.column_dimensions['C'].width = 15
            ws_details.column_dimensions['D'].width = 15
            ws_details.column_dimensions['E'].width = 12
            
            # Format Summary Sheet
            ws_summary = writer.sheets['Summary']
            ws_summary.column_dimensions['A'].width = 25
            ws_summary.column_dimensions['B'].width = 25
            
        return str(filepath)
