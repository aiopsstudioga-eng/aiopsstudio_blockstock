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
