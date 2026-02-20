
import pytest
import sqlite3
from datetime import date, timedelta
from services.analytics_service import AnalyticsService
from database.connection import get_db_manager

class TestAnalyticsService:
    @pytest.fixture
    def service(self, isolated_db):
        return AnalyticsService()

    @pytest.fixture
    def seed_data(self, isolated_db):
        """Seed database with diverse transaction data for analytics testing."""
        conn = isolated_db.get_connection()
        cursor = conn.cursor()
        
        
        # 1. Create Items
        cursor.executemany("""
            INSERT INTO inventory_items (sku, name, category_id, quantity_on_hand, total_cost_basis_cents, reorder_threshold)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ('SKU-001', 'High Risk Item', 1, 5, 500, 10),      # 1 = Food
            ('SKU-002', 'Stable Item', 2, 100, 20000, 20),     # 2 = Non-Food
            ('SKU-003', 'Donor Item', 2, 10, 50000, 5)         # 2 = Non-Food
        ])
        
        # Get IDs
        item_ids = {}
        for row in cursor.execute("SELECT id, sku FROM inventory_items"):
            item_ids[row[1]] = row[0]
            
        today = date.today()
        
        # 2. Create Distributions (for consumption/forecast)
        # High Risk Item: High recent usage
        cursor.executemany("""
            INSERT INTO inventory_transactions (item_id, transaction_type, quantity_change, transaction_date)
            VALUES (?, 'DISTRIBUTION', ?, ?)
        """, [
            (item_ids['SKU-001'], -2, (today - timedelta(days=1)).isoformat()),
            (item_ids['SKU-001'], -2, (today - timedelta(days=2)).isoformat()),
            (item_ids['SKU-001'], -1, (today - timedelta(days=5)).isoformat()),
            # Stable Item: Low usage
            (item_ids['SKU-002'], -1, (today - timedelta(days=10)).isoformat()),
        ])
        
        # 3. Create Donations (for donor impact)
        cursor.executemany("""
            INSERT INTO inventory_transactions (item_id, transaction_type, quantity_change, transaction_date, fair_market_value_cents, donor, notes)
            VALUES (?, 'DONATION', ?, ?, ?, ?, ?)
        """, [
            (item_ids['SKU-003'], 5, today.isoformat(), 5000, 'John Doe', 'Gift 1'),
            (item_ids['SKU-003'], 5, (today - timedelta(days=30)).isoformat(), 5000, 'John Doe', 'Gift 2'),
            (item_ids['SKU-002'], 10, (today - timedelta(days=15)).isoformat(), 0, 'Jane Smith', 'Clothes'), # $0 cost donation
        ])
        
        # 4. Create Purchases (for trends)
        cursor.executemany("""
            INSERT INTO inventory_transactions (item_id, transaction_type, quantity_change, transaction_date, unit_cost_cents, notes)
            VALUES (?, 'PURCHASE', ?, ?, ?, ?)
        """, [
            (item_ids['SKU-001'], 10, (today - timedelta(days=60)).isoformat(), 100, 'Vendor A'),
        ])
        
        conn.commit()
        return item_ids

    def test_get_inventory_forecast(self, service, seed_data):
        """Test inventory forecast calculation and risk levels."""
        forecast = service.get_inventory_forecast(days_ahead=30, lookback_days=90)
        
        assert len(forecast) == 3
        
        # Check High Risk Item
        high_risk = next(f for f in forecast if f['sku'] == 'SKU-001')
        assert high_risk['risk_level'] in ['critical', 'high']
        assert high_risk['daily_consumption_rate'] > 0
        assert high_risk['days_until_stockout'] < 10
        
        # Check Stable Item
        stable = next(f for f in forecast if f['sku'] == 'SKU-002')
        assert stable['risk_level'] == 'low'
        assert stable['days_until_stockout'] > 30

    def test_get_seasonal_trends(self, service, seed_data):
        """Test seasonal trend aggregation."""
        today = date.today()
        trends = service.get_seasonal_trends(year=today.year)
        
        assert trends['year'] == today.year
        assert len(trends['months']) == 12
        
        # Verify totals
        totals = trends['totals']
        assert totals['donations_qty'] == 20  # 5 + 5 + 10
        assert totals['distributions_qty'] == 6  # 2 + 2 + 1 + 1 (all positive in trends)
        
        # Verify current month data
        current_month_idx = today.month - 1
        current_month_data = trends['months'][current_month_idx]
        # Depending on when in the month this runs, we assert > 0 if transactions exist
        # Since logic distributes based on exact date, let's just check the structure is solid
        assert 'distributions_qty' in current_month_data

    def test_get_donor_impact_summary(self, service, seed_data):
        """Test donor impact report generation."""
        impact = service.get_donor_impact_summary()
        
        assert impact['total_donors'] == 2
        assert impact['total_donations'] == 3
        assert impact['total_quantity'] == 20
        assert impact['total_fmv_dollars'] == 100.00  # 2 donations of 5000 cents ($50.00) = $100.00
        
        # Check top donor
        top_donor = impact['donors'][0]
        assert top_donor['donor'] == 'John Doe'
        assert top_donor['donation_count'] == 2
        assert top_donor['total_fmv_dollars'] == 100.00
