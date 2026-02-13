"""
Reporting service for AIOps Studio - Inventory.

Generates financial, impact, and stock status reports.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from pathlib import Path

from models.item import InventoryItem
from models.transaction import Transaction, TransactionType
from database.connection import get_db_manager


class ReportingService:
    """Service layer for generating reports."""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        Initialize reporting service.
        
        Args:
            db_path: Path to the database file
        """
        self.db_manager = get_db_manager(db_path)
    
    # ========================================================================
    # FINANCIAL REPORT - COST OF GOODS DISTRIBUTED (COGS)
    # ========================================================================
    
    def get_financial_report_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get financial report data (COGS).
        
        Args:
            start_date: Start date (optional, defaults to beginning of time)
            end_date: End date (optional, defaults to now)
            
        Returns:
            Dict with financial data
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Build query with date filters
        query = """
            SELECT 
                ii.name,
                ii.sku,
                it.transaction_date,
                it.quantity_change,
                it.unit_cost_cents,
                it.total_financial_impact_cents,
                it.reason_code
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            WHERE it.transaction_type = 'DISTRIBUTION'
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY it.transaction_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Calculate totals
        total_cogs_cents = 0
        client_cogs_cents = 0
        spoilage_cogs_cents = 0
        internal_cogs_cents = 0
        
        distributions = []
        
        for row in rows:
            cogs_cents = row['total_financial_impact_cents']
            total_cogs_cents += cogs_cents
            
            # Categorize by reason
            reason = row['reason_code']
            if reason == 'CLIENT':
                client_cogs_cents += cogs_cents
            elif reason == 'SPOILAGE':
                spoilage_cogs_cents += cogs_cents
            elif reason == 'INTERNAL':
                internal_cogs_cents += cogs_cents
            
            distributions.append({
                'item_name': row['name'],
                'sku': row['sku'],
                'date': row['transaction_date'],
                'quantity': abs(row['quantity_change']),
                'unit_cost_cents': row['unit_cost_cents'],
                'total_cogs_cents': cogs_cents,
                'reason': reason
            })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_cogs_cents': total_cogs_cents,
            'total_cogs_dollars': total_cogs_cents / 100.0,
            'client_cogs_cents': client_cogs_cents,
            'client_cogs_dollars': client_cogs_cents / 100.0,
            'spoilage_cogs_cents': spoilage_cogs_cents,
            'spoilage_cogs_dollars': spoilage_cogs_cents / 100.0,
            'internal_cogs_cents': internal_cogs_cents,
            'internal_cogs_dollars': internal_cogs_cents / 100.0,
            'distributions': distributions,
            'distribution_count': len(distributions)
        }
    
    # ========================================================================
    # IMPACT REPORT - FAIR MARKET VALUE
    # ========================================================================
    
    def get_impact_report_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get impact report data (donations and FMV).
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Dict with impact data
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get donations
        query = """
            SELECT 
                ii.name,
                ii.sku,
                it.transaction_date,
                it.quantity_change,
                it.fair_market_value_cents,
                it.donor
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            WHERE it.transaction_type = 'DONATION'
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY it.transaction_date DESC"
        
        cursor.execute(query, params)
        donation_rows = cursor.fetchall()
        
        # Get distributions for total value distributed
        dist_query = """
            SELECT 
                ii.name,
                ii.sku,
                it.transaction_date,
                it.quantity_change,
                it.total_financial_impact_cents,
                it.reason_code
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            WHERE it.transaction_type = 'DISTRIBUTION'
            AND it.reason_code = 'CLIENT'
        """
        
        dist_params = []
        
        if start_date:
            dist_query += " AND DATE(it.transaction_date) >= ?"
            dist_params.append(start_date.isoformat())
        
        if end_date:
            dist_query += " AND DATE(it.transaction_date) <= ?"
            dist_params.append(end_date.isoformat())
        
        cursor.execute(dist_query, dist_params)
        dist_rows = cursor.fetchall()
        
        # Calculate totals
        total_fmv_cents = sum(row['fair_market_value_cents'] for row in donation_rows)
        total_distributed_value_cents = sum(row['total_financial_impact_cents'] for row in dist_rows)
        
        donations = []
        for row in donation_rows:
            donations.append({
                'item_name': row['name'],
                'sku': row['sku'],
                'date': row['transaction_date'],
                'quantity': row['quantity_change'],
                'fmv_cents': row['fair_market_value_cents'],
                'donor': row['donor']
            })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_donations_fmv_cents': total_fmv_cents,
            'total_donations_fmv_dollars': total_fmv_cents / 100.0,
            'total_distributed_value_cents': total_distributed_value_cents,
            'total_distributed_value_dollars': total_distributed_value_cents / 100.0,
            'donations': donations,
            'donation_count': len(donations),
            'distributions_count': len(dist_rows)
        }
    
    # ========================================================================
    # STOCK STATUS REPORT
    # ========================================================================
    
    def get_stock_status_data(self) -> Dict:
        """
        Get stock status report data.
        
        Returns:
            Dict with stock status data
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get all active items with their status
        cursor.execute("""
            SELECT 
                id,
                sku,
                name,
                quantity_on_hand,
                reorder_threshold,
                total_cost_basis_cents,
                category_id
            FROM inventory_items
            WHERE is_active = 1
            ORDER BY name
        """)
        
        rows = cursor.fetchall()
        
        items_below_threshold = []
        items_zero_stock = []
        items_ok = []
        
        total_items = len(rows)
        total_value_cents = 0
        
        for row in rows:
            qty = row['quantity_on_hand']
            threshold = row['reorder_threshold']
            cost_basis = row['total_cost_basis_cents']
            
            total_value_cents += cost_basis
            
            item_data = {
                'sku': row['sku'],
                'name': row['name'],
                'quantity': qty,
                'threshold': threshold,
                'value_cents': cost_basis,
                'unit_cost_cents': int(cost_basis / qty) if qty > 0 else 0
            }
            
            if qty == 0:
                items_zero_stock.append(item_data)
            elif qty < threshold:
                items_below_threshold.append(item_data)
            else:
                items_ok.append(item_data)
        
        return {
            'total_items': total_items,
            'total_value_cents': total_value_cents,
            'total_value_dollars': total_value_cents / 100.0,
            'items_ok': items_ok,
            'items_below_threshold': items_below_threshold,
            'items_zero_stock': items_zero_stock,
            'ok_count': len(items_ok),
            'below_threshold_count': len(items_below_threshold),
            'zero_stock_count': len(items_zero_stock)
        }
    
    # ========================================================================
    # TRANSACTION HISTORY
    # ========================================================================
    
    def get_transaction_history(
        self,
        item_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: Optional[int] = 100
    ) -> List[Dict]:
        """
        Get transaction history.
        
        Args:
            item_id: Filter by item ID (optional)
            start_date: Start date (optional)
            end_date: End date (optional)
            limit: Maximum number of transactions
            
        Returns:
            List of transaction dicts
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                it.*,
                ii.name as item_name,
                ii.sku
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            WHERE 1=1
        """
        
        params = []
        
        if item_id:
            query += " AND it.item_id = ?"
            params.append(item_id)
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY it.transaction_date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row['id'],
                'item_name': row['item_name'],
                'sku': row['sku'],
                'type': row['transaction_type'],
                'date': row['transaction_date'],
                'quantity': row['quantity_change'],
                'unit_cost_cents': row['unit_cost_cents'],
                'fmv_cents': row['fair_market_value_cents'],
                'cogs_cents': row['total_financial_impact_cents'],
                'reason': row['reason_code'],
                'supplier': row['supplier'],
                'donor': row['donor'],
                'notes': row['notes']
            })
        
        return transactions
    
    # ========================================================================
    # DASHBOARD STATISTICS
    # ========================================================================
    
    def get_dashboard_stats(self) -> Dict:
        """
        Get aggregated statistics for the dashboard.
        
        Returns:
            Dict containing:
            - total_inventory_value_dollars
            - low_stock_count
            - total_items_count
            - top_distributed_items (list)
            - value_by_category (list)
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # 1. Total Inventory Value & Item Counts
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                SUM(CASE WHEN quantity_on_hand < reorder_threshold THEN 1 ELSE 0 END) as low_stock,
                SUM(total_cost_basis_cents) as total_value_cents
            FROM inventory_items
            WHERE is_active = 1
        """)
        row = cursor.fetchone()
        stats['total_items_count'] = row['total_items']
        stats['low_stock_count'] = row['low_stock']
        stats['total_inventory_value_dollars'] = (row['total_value_cents'] or 0) / 100.0
        
        # 2. Value by Category
        cursor.execute("""
            SELECT 
                c.name,
                SUM(i.total_cost_basis_cents) as value_cents
            FROM inventory_items i
            JOIN item_categories c ON i.category_id = c.id
            WHERE i.is_active = 1
            GROUP BY c.name
            HAVING value_cents > 0
            ORDER BY value_cents DESC
        """)
        stats['value_by_category'] = [
            {'category': row['name'], 'value_dollars': row['value_cents'] / 100.0}
            for row in cursor.fetchall()
        ]
        
        # 3. Top Distributed Items (All Time)
        cursor.execute("""
            SELECT 
                i.name,
                ABS(SUM(t.quantity_change)) as total_distributed
            FROM inventory_transactions t
            JOIN inventory_items i ON t.item_id = i.id
            WHERE t.transaction_type = 'DISTRIBUTION'
            GROUP BY i.name
            ORDER BY total_distributed DESC
            LIMIT 5
        """)
        stats['top_distributed_items'] = [
            {'name': row['name'], 'quantity': row['total_distributed']}
            for row in cursor.fetchall()
        ]
        
        return stats
    
    # ========================================================================
    # PURCHASES REPORT
    # ========================================================================
    
    def get_purchases_report_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get purchases report data.
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Dict with purchases data
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get purchases
        query = """
            SELECT 
                ii.name,
                ii.sku,
                ic.name as category_name,
                it.transaction_date,
                it.quantity_change,
                it.unit_cost_cents,
                it.supplier,
                it.notes
            FROM inventory_transactions it
            JOIN inventory_items ii ON it.item_id = ii.id
            LEFT JOIN item_categories ic ON ii.category_id = ic.id
            WHERE it.transaction_type = 'PURCHASE'
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY it.transaction_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Calculate totals
        total_purchases = len(rows)
        total_quantity = 0
        total_cost_cents = 0
        suppliers_set = set()
        
        purchases = []
        
        for row in rows:
            qty = row['quantity_change']
            unit_cost = row['unit_cost_cents']
            total_item_cost = int(qty * unit_cost)
            
            total_quantity += qty
            total_cost_cents += total_item_cost
            
            if row['supplier']:
                suppliers_set.add(row['supplier'])
            
            purchases.append({
                'item_name': row['name'],
                'sku': row['sku'],
                'category': row['category_name'] or 'Uncategorized',
                'date': row['transaction_date'],
                'quantity': qty,
                'unit_cost_cents': unit_cost,
                'total_cost_cents': total_item_cost,
                'supplier': row['supplier'],
                'notes': row['notes']
            })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_purchases': total_purchases,
            'total_quantity': total_quantity,
            'total_cost_cents': total_cost_cents,
            'total_cost_dollars': total_cost_cents / 100.0,
            'unique_suppliers': len(suppliers_set),
            'purchases': purchases
        }
    
    # ========================================================================
    # SUPPLIERS REPORT
    # ========================================================================
    
    def get_suppliers_report_data(self) -> Dict:
        """
        Get suppliers report data.
        
        Returns:
            Dict with suppliers data including aggregated purchases and notes
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get all suppliers with aggregated data
        cursor.execute("""
            SELECT 
                it.supplier,
                COUNT(*) as purchase_count,
                SUM(it.quantity_change) as total_quantity,
                SUM(it.quantity_change * it.unit_cost_cents) as total_cost_cents,
                MIN(it.transaction_date) as first_purchase,
                MAX(it.transaction_date) as last_purchase,
                GROUP_CONCAT(it.notes, ' | ') as all_notes
            FROM inventory_transactions it
            WHERE it.transaction_type = 'PURCHASE'
            AND it.supplier IS NOT NULL
            AND it.supplier != ''
            GROUP BY it.supplier
            ORDER BY total_cost_cents DESC
        """)
        
        rows = cursor.fetchall()
        
        suppliers = []
        total_suppliers = len(rows)
        grand_total_purchases = 0
        grand_total_cost_cents = 0
        
        for row in rows:
            total_cost = row['total_cost_cents'] or 0
            grand_total_purchases += row['purchase_count']
            grand_total_cost_cents += total_cost
            
            # Clean up notes - remove None values and duplicates
            notes_str = row['all_notes'] or ''
            if notes_str:
                # Split by separator, remove empty/None, and keep unique
                notes_list = [n.strip() for n in notes_str.split('|') if n and n.strip() and n.strip().lower() != 'none']
                unique_notes = list(dict.fromkeys(notes_list))  # Preserve order while removing duplicates
                cleaned_notes = ' | '.join(unique_notes) if unique_notes else ''
            else:
                cleaned_notes = ''
            
            suppliers.append({
                'supplier': row['supplier'],
                'purchase_count': row['purchase_count'],
                'total_quantity': row['total_quantity'],
                'total_cost_cents': total_cost,
                'total_cost_dollars': total_cost / 100.0,
                'first_purchase': row['first_purchase'],
                'last_purchase': row['last_purchase'],
                'notes': cleaned_notes
            })
        
        return {
            'total_suppliers': total_suppliers,
            'total_purchases': grand_total_purchases,
            'total_cost_cents': grand_total_cost_cents,
            'total_cost_dollars': grand_total_cost_cents / 100.0,
            'suppliers': suppliers
        }
