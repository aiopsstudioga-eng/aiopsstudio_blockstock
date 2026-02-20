"""
Analytics service for AIOps Studio - Inventory.

Provides predictive forecasting, seasonal trend analysis, and donor impact tracking.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from collections import defaultdict

from database.connection import get_db_manager


class AnalyticsService:
    """Service layer for advanced analytics and forecasting."""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        Initialize analytics service.
        
        Args:
            db_path: Path to the database file
        """
        self.db_manager = get_db_manager(db_path)
    
    # =========================================================================
    # PREDICTIVE INVENTORY FORECASTING
    # =========================================================================
    
    def get_inventory_forecast(
        self,
        days_ahead: int = 30,
        lookback_days: int = 90
    ) -> List[Dict]:
        """
        Calculate inventory forecast for each item.
        
        Uses weighted moving average of recent consumption patterns to predict
        future inventory levels and identify stockout risks.
        
        Args:
            days_ahead: Number of days to forecast ahead (configurable)
            lookback_days: Number of historical days to analyze
            
        Returns:
            List of forecast data for each item
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        # Get all active items with current inventory
        cursor.execute("""
            SELECT 
                id, sku, name, category_id,
                quantity_on_hand, reorder_threshold,
                total_cost_basis_cents
            FROM inventory_items
            WHERE is_active = 1 AND quantity_on_hand > 0
            ORDER BY name
        """)
        items = cursor.fetchall()
        
        # Get distribution history for the lookback period
        cursor.execute("""
            SELECT 
                item_id,
                DATE(transaction_date) as dist_date,
                SUM(ABS(quantity_change)) as total_quantity
            FROM inventory_transactions
            WHERE transaction_type = 'DISTRIBUTION'
              AND is_voided = 0
              AND transaction_date >= ?
            GROUP BY item_id, DATE(transaction_date)
        """, (start_date.isoformat(),))
        
        # Organize distribution data by item_id
        dist_data = defaultdict(list)
        for row in cursor.fetchall():
            dist_data[row['item_id']].append({
                'date': datetime.strptime(row['dist_date'], '%Y-%m-%d').date(),
                'quantity': row['total_quantity']
            })
        
        forecasts = []
        
        for item in items:
            item_id = item['id']
            current_qty = item['quantity_on_hand']
            threshold = item['reorder_threshold']
            
            # Calculate consumption rate
            item_dist = dist_data.get(item_id, [])
            
            if not item_dist:
                # No distribution history - assume stable
                daily_rate = 0.0
                confidence = "low"
            else:
                # Calculate daily consumption using weighted moving average
                daily_rate, confidence = self._calculate_consumption_rate(
                    item_dist, lookback_days
                )
            
            # Project future inventory
            projected_qty = current_qty - (daily_rate * days_ahead)
            days_until_stockout = float('inf') if daily_rate == 0 else current_qty / daily_rate if daily_rate > 0 else float('inf')
            
            # Determine risk level
            if daily_rate == 0:
                risk_level = "low"
            elif projected_qty <= 0:
                risk_level = "critical"
            elif projected_qty < threshold:
                risk_level = "high"
            elif projected_qty < threshold * 2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            forecasts.append({
                'item_id': item_id,
                'sku': item['sku'],
                'name': item['name'],
                'current_quantity': current_qty,
                'reorder_threshold': threshold,
                'daily_consumption_rate': round(daily_rate, 2),
                'projected_quantity': round(max(0, projected_qty), 2),
                'days_until_stockout': int(days_until_stockout) if days_until_stockout != float('inf') else None,
                'days_ahead': days_ahead,
                'risk_level': risk_level,
                'confidence': confidence,
                'lookback_days': lookback_days
            })
        
        # Sort by risk level (critical first)
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        forecasts.sort(key=lambda x: (risk_order.get(x['risk_level'], 4), x['name']))
        
        return forecasts
    
    def _calculate_consumption_rate(
        self,
        dist_data: List[Dict],
        total_days: int
    ) -> Tuple[float, str]:
        """
        Calculate weighted daily consumption rate.
        
        Uses exponential weighting - more recent data has higher weight.
        
        Args:
            dist_data: List of distribution dicts with 'date' and 'quantity'
            total_days: Total period in days
            
        Returns:
            Tuple of (daily_rate, confidence_level)
        """
        if not dist_data:
            return 0.0, "low"
        
        # Sort by date
        dist_data.sort(key=lambda x: x['date'])
        
        # Calculate weights (exponential decay)
        n = len(dist_data)
        weights = [0.7 ** (n - 1 - i) for i in range(n)]
        total_weight = sum(weights)
        
        # Weighted average daily consumption
        total_distributed = sum(d['quantity'] * w for d, w in zip(dist_data, weights))
        daily_rate = total_distributed / total_weight if total_weight > 0 else 0
        
        # Determine confidence based on data density
        if n >= 30:
            confidence = "high"
        elif n >= 10:
            confidence = "medium"
        else:
            confidence = "low"
        
        return daily_rate, confidence
    
    def get_stockout_risk_items(
        self,
        days_ahead: int = 30,
        lookback_days: int = 90
    ) -> List[Dict]:
        """
        Get items at risk of stockout.
        
        Args:
            days_ahead: Forecast period
            lookback_days: Historical analysis period
            
        Returns:
            List of items at risk, sorted by severity
        """
        forecasts = self.get_inventory_forecast(days_ahead, lookback_days)
        
        # Filter to at-risk items
        at_risk = [
            f for f in forecasts 
            if f['risk_level'] in ('critical', 'high', 'medium')
        ]
        
        return at_risk
    
    # =========================================================================
    # SEASONAL TREND ANALYSIS
    # =========================================================================
    
    def get_seasonal_trends(
        self,
        year: Optional[int] = None,
        include_distributions: bool = True,
        include_donations: bool = True,
        include_purchases: bool = True
    ) -> Dict:
        """
        Analyze seasonal trends by month.
        
        Args:
            year: Year to analyze (defaults to current year)
            include_distributions: Include distribution data
            include_donations: Include donation data
            include_purchases: Include purchase data
            
        Returns:
            Dict with monthly aggregates
        """
        if year is None:
            year = datetime.now().year
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        monthly_data = defaultdict(lambda: {
            'distributions_qty': 0,
            'distributions_value': 0,
            'donations_qty': 0,
            'donations_value': 0,
            'purchases_qty': 0,
            'purchases_value': 0
        })
        
        # Distribution trends
        if include_distributions:
            cursor.execute("""
                SELECT 
                    strftime('%m', transaction_date) as month,
                    SUM(ABS(quantity_change)) as quantity,
                    SUM(ABS(total_financial_impact_cents)) as value
                FROM inventory_transactions
                WHERE transaction_type = 'DISTRIBUTION'
                  AND is_voided = 0
                  AND transaction_date >= ? 
                  AND transaction_date <= ?
                GROUP BY strftime('%m', transaction_date)
            """, (start_date, end_date))
            
            for row in cursor.fetchall():
                month = int(row['month'])
                monthly_data[month]['distributions_qty'] = row['quantity'] or 0
                monthly_data[month]['distributions_value'] = (row['value'] or 0) / 100.0
        
        # Donation trends
        if include_donations:
            cursor.execute("""
                SELECT 
                    strftime('%m', transaction_date) as month,
                    SUM(quantity_change) as quantity,
                    SUM(fair_market_value_cents) as value
                FROM inventory_transactions
                WHERE transaction_type = 'DONATION'
                  AND is_voided = 0
                  AND transaction_date >= ? 
                  AND transaction_date <= ?
                GROUP BY strftime('%m', transaction_date)
            """, (start_date, end_date))
            
            for row in cursor.fetchall():
                month = int(row['month'])
                monthly_data[month]['donations_qty'] = row['quantity'] or 0
                monthly_data[month]['donations_value'] = (row['value'] or 0) / 100.0
        
        # Purchase trends
        if include_purchases:
            cursor.execute("""
                SELECT 
                    strftime('%m', transaction_date) as month,
                    SUM(quantity_change) as quantity,
                    SUM(quantity_change * unit_cost_cents) as value
                FROM inventory_transactions
                WHERE transaction_type = 'PURCHASE'
                  AND is_voided = 0
                  AND transaction_date >= ? 
                  AND transaction_date <= ?
                GROUP BY strftime('%m', transaction_date)
            """, (start_date, end_date))
            
            for row in cursor.fetchall():
                month = int(row['month'])
                monthly_data[month]['purchases_qty'] = row['quantity'] or 0
                monthly_data[month]['purchases_value'] = (row['value'] or 0) / 100.0
        
        # Format results
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        trends = []
        for month_num in range(1, 13):
            data = monthly_data[month_num]
            trends.append({
                'month': month_num,
                'month_name': month_names[month_num - 1],
                'distributions_qty': data['distributions_qty'],
                'distributions_value': round(data['distributions_value'], 2),
                'donations_qty': data['donations_qty'],
                'donations_value': round(data['donations_value'], 2),
                'purchases_qty': data['purchases_qty'],
                'purchases_value': round(data['purchases_value'], 2),
                'total_inflow': data['donations_qty'] + data['purchases_qty'],
                'total_outflow': data['distributions_qty']
            })
        
        # Calculate totals
        totals = {
            'distributions_qty': sum(t['distributions_qty'] for t in trends),
            'distributions_value': sum(t['distributions_value'] for t in trends),
            'donations_qty': sum(t['donations_qty'] for t in trends),
            'donations_value': sum(t['donations_value'] for t in trends),
            'purchases_qty': sum(t['purchases_qty'] for t in trends),
            'purchases_value': sum(t['purchases_value'] for t in trends)
        }
        
        # Find peak month
        peak_month = max(trends, key=lambda x: x['distributions_qty'])
        
        return {
            'year': year,
            'months': trends,
            'totals': totals,
            'peak_month': peak_month['month_name'],
            'peak_distribution_qty': peak_month['distributions_qty']
        }
    
    def get_year_over_year_comparison(
        self,
        years: Optional[List[int]] = None
    ) -> Dict:
        """
        Compare metrics across multiple years.
        
        Args:
            years: List of years to compare (defaults to last 3 years)
            
        Returns:
            Dict with year-over-year comparison data
        """
        if years is None:
            current_year = datetime.now().year
            years = [current_year - 2, current_year - 1, current_year]
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        comparison = {}
        
        for year in years:
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            
            # Get summary stats
            cursor.execute("""
                SELECT 
                    transaction_type,
                    SUM(ABS(quantity_change)) as total_quantity,
                    SUM(ABS(total_financial_impact_cents)) as total_value
                FROM inventory_transactions
                WHERE is_voided = 0
                  AND transaction_date >= ?
                  AND transaction_date <= ?
                GROUP BY transaction_type
            """, (start_date, end_date))
            
            stats = {
                'distributions_qty': 0,
                'distributions_value': 0,
                'donations_qty': 0,
                'donations_value': 0,
                'purchases_qty': 0,
                'purchases_value': 0,
                'total_transactions': 0
            }
            
            for row in cursor.fetchall():
                qty = row['total_quantity'] or 0
                val = (row['total_value'] or 0) / 100.0
                stats['total_transactions'] += 1
                
                if row['transaction_type'] == 'DISTRIBUTION':
                    stats['distributions_qty'] = qty
                    stats['distributions_value'] = val
                elif row['transaction_type'] == 'DONATION':
                    stats['donations_qty'] = qty
                    stats['donations_value'] = val
                elif row['transaction_type'] == 'PURCHASE':
                    stats['purchases_qty'] = qty
                    stats['purchases_value'] = val
            
            comparison[year] = stats
        
        # Calculate YoY changes
        years_sorted = sorted(comparison.keys())
        yoy_changes = {}
        
        for i, year in enumerate(years_sorted):
            if i == 0:
                yoy_changes[year] = None  # No comparison for first year
            else:
                prev_year = years_sorted[i - 1]
                prev = comparison[prev_year]
                curr = comparison[year]
                
                if prev['distributions_qty'] > 0:
                    dist_pct = ((curr['distributions_qty'] - prev['distributions_qty']) 
                               / prev['distributions_qty'] * 100)
                else:
                    dist_pct = 0
                
                yoy_changes[year] = round(dist_pct, 1)
        
        return {
            'years': years_sorted,
            'data': comparison,
            'yoy_changes': yoy_changes
        }
    
    # =========================================================================
    # CATEGORY TRENDS
    # =========================================================================
    
    def get_category_trends(
        self,
        year: Optional[int] = None
    ) -> Dict:
        """
        Get distribution trends by category.
        
        Args:
            year: Year to analyze
            
        Returns:
            Dict with category-level trends
        """
        if year is None:
            year = datetime.now().year
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        cursor.execute("""
            SELECT 
                ic.name as category_name,
                ic.id as category_id,
                SUM(ABS(it.quantity_change)) as total_distributed,
                SUM(ABS(it.total_financial_impact_cents)) as total_value
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            LEFT JOIN item_categories ic ON ii.category_id = ic.id
            WHERE it.transaction_type = 'DISTRIBUTION'
              AND it.is_voided = 0
              AND it.transaction_date >= ?
              AND it.transaction_date <= ?
            GROUP BY ic.id
            ORDER BY total_distributed DESC
        """, (start_date, end_date))
        
        categories = []
        total_qty = 0
        total_value = 0
        
        for row in cursor.fetchall():
            qty = row['total_distributed'] or 0
            val = (row['total_value'] or 0) / 100.0
            
            total_qty += qty
            total_value += val
            
            categories.append({
                'category_id': row['category_id'],
                'category_name': row['category_name'] or 'Uncategorized',
                'quantity': qty,
                'value': round(val, 2),
                'percentage': 0  # Will calculate after
            })
        
        # Calculate percentages
        for cat in categories:
            if total_qty > 0:
                cat['percentage'] = round((cat['quantity'] / total_qty) * 100, 1)
            else:
                cat['percentage'] = 0
        
        return {
            'year': year,
            'categories': categories,
            'total_quantity': total_qty,
            'total_value': round(total_value, 2)
        }
    
    # =========================================================================
    # DONOR IMPACT TRACKING
    # =========================================================================
    
    def get_donor_impact_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get summary of donor impact.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dict with donor impact data
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                donor,
                COUNT(*) as donation_count,
                SUM(quantity_change) as total_quantity,
                SUM(fair_market_value_cents) as total_fmv_cents
            FROM inventory_transactions
            WHERE transaction_type = 'DONATION'
              AND is_voided = 0
              AND donor IS NOT NULL
              AND donor != ''
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(transaction_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND DATE(transaction_date) <= ?"
            params.append(end_date.isoformat())
        
        query += " GROUP BY donor ORDER BY total_fmv_cents DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        donors = []
        total_fmv_cents = 0
        total_quantity = 0
        
        for row in rows:
            fmv = row['total_fmv_cents'] or 0
            qty = row['total_quantity'] or 0
            
            total_fmv_cents += fmv
            total_quantity += qty
            
            donors.append({
                'donor': row['donor'],
                'donation_count': row['donation_count'],
                'total_quantity': qty,
                'total_fmv_cents': fmv,
                'total_fmv_dollars': round(fmv / 100.0, 2)
            })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_donors': len(donors),
            'total_donations': sum(d['donation_count'] for d in donors),
            'total_quantity': total_quantity,
            'total_fmv_cents': total_fmv_cents,
            'total_fmv_dollars': round(total_fmv_cents / 100.0, 2),
            'donors': donors
        }
    
    def get_top_donors(
        self,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get top donors by fair market value.
        
        Args:
            limit: Number of donors to return
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of top donors
        """
        summary = self.get_donor_impact_summary(start_date, end_date)
        return summary['donors'][:limit]
    
    def get_donor_retention(
        self,
        years: int = 2
    ) -> Dict:
        """
        Analyze donor retention over time.
        
        Args:
            years: Number of years to analyze
            
        Returns:
            Dict with retention metrics
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        current_year = datetime.now().year
        start_year = current_year - years + 1
        
        # Get unique donors per year
        yearly_donors = {}
        
        for year in range(start_year, current_year + 1):
            cursor.execute("""
                SELECT DISTINCT donor
                FROM inventory_transactions
                WHERE transaction_type = 'DONATION'
                  AND is_voided = 0
                  AND donor IS NOT NULL
                  AND donor != ''
                  AND strftime('%Y', transaction_date) = ?
            """, (str(year),))
            
            donors = {row['donor'] for row in cursor.fetchall()}
            yearly_donors[year] = donors
        
        # Calculate retention
        retention_data = []
        
        for i, year in enumerate(range(start_year, current_year + 1)):
            current_set = yearly_donors.get(year, set())
            
            if i == 0:
                new_donors = len(current_set)
                returning_donors = 0
            else:
                prev_year = year - 1
                prev_donors = yearly_donors.get(prev_year, set())
                
                returning = current_set & prev_donors
                new_donors = len(current_set - prev_donors)
                returning_donors = len(returning)
            
            retention_data.append({
                'year': year,
                'total_donors': len(current_set),
                'new_donors': new_donors,
                'returning_donors': returning_donors,
                'retention_rate': round((returning_donors / len(current_set) * 100) 
                                       if len(current_set) > 0 else 0, 1) if i > 0 else None
            })
        
        return {
            'years_analyzed': years,
            'retention_data': retention_data
        }
