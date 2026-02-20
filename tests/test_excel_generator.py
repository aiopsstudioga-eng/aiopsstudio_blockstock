
import pytest
import os
import pandas as pd
from pathlib import Path
from services.excel_generator import ExcelReportGenerator
from datetime import date

class TestExcelReportGenerator:
    @pytest.fixture
    def generator(self, tmp_path):
        return ExcelReportGenerator(output_dir=tmp_path)

    def test_generate_inventory_forecast_report(self, generator):
        """Test forecast report generation."""
        data = [{
            'sku': 'SKU-001',
            'name': 'Test Item', # Fixed key based on previous bug fix
            'item_name': 'Test Item', # Also include just in case, but expecting 'name' used in generator
            'current_quantity': 100,
            'daily_consumption_rate': 2.5,
            'projected_quantity': 25,
            'days_until_stockout': 10,
            'risk_level': 'high',
            'confidence': 'medium'
        }]
        
        filepath = generator.generate_inventory_forecast_report(data)
        assert os.path.exists(filepath)
        
        # Verify content
        try:
            df = pd.read_excel(filepath, sheet_name='Forecast')
            assert len(df) == 1
            assert df.iloc[0]['SKU'] == 'SKU-001'
            assert df.iloc[0]['Risk Level'] == 'HIGH'
        except ImportError:
            pytest.skip("pandas/openpyxl not installed for reading, but file exists")

    def test_generate_seasonal_trends_report(self, generator):
        """Test trends report generation."""
        data = {
            'year': 2026,
            'peak_month': 'December',
            'peak_distribution_qty': 500,
            'totals': {
                'distributions_qty': 1000,
                'distributions_value': 5000.0,
                'donations_qty': 200,
                'donations_value': 0.0,
                'purchases_qty': 800,
                'purchases_value': 4000.0
            },
            'months': [
                {
                    'month_name': 'January',
                    'distributions_qty': 100, 'distributions_value': 500.0,
                    'donations_qty': 20, 'donations_value': 0.0,
                    'purchases_qty': 80, 'purchases_value': 400.0
                }
            ]
        }
        
        filepath = generator.generate_seasonal_trends_report(data)
        assert os.path.exists(filepath)
        
        try:
            df = pd.read_excel(filepath, sheet_name='Summary')
            assert df.iloc[3]['Value'] == 'December'
        except ImportError:
            pass

    def test_generate_donor_impact_report(self, generator):
        """Test donor impact report generation."""
        data = {
            'total_donors': 5,
            'total_donations': 10,
            'total_quantity': 100,
            'total_fmv_cents': 50000,
            'total_fmv_dollars': 500.00,
            'donors': [
                {
                    'donor': 'Donor A',
                    'donation_count': 2,
                    'total_quantity': 20,
                    'total_fmv_cents': 10000,
                    'total_fmv_dollars': 100.00
                }
            ]
        }
        
        filepath = generator.generate_donor_impact_report(data)
        assert os.path.exists(filepath)
        
        try:
            df = pd.read_excel(filepath, sheet_name='Donor Details')
            assert df.iloc[0]['Donor Name'] == 'Donor A'
            assert df.iloc[0]['% of Total'] == '20.0%'
        except ImportError:
            pass
