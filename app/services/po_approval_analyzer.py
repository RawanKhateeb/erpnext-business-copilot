"""
Purchase Order Approval Analyzer

Analyzes POs to recommend APPROVE/REVIEW/DO NOT APPROVE decisions based on:
1. Price reasonability (item rate vs historical average)
2. Supplier risk (open orders, delays, pricing anomalies)
3. Missing data validation
"""

from typing import Dict, List, Any, Tuple
from app.models.erp_client import ERPNextClient


def get_supplier_open_orders(client: ERPNextClient, supplier: str) -> int:
    """Count open purchase orders for a supplier."""
    try:
        pos = client.list_purchase_orders(limit=100)
        if not pos:
            return 0
        
        open_count = sum(1 for p in pos 
                        if p.get('supplier') == supplier 
                        and p.get('status') not in ['Completed', 'Cancelled'])
        return open_count
    except:
        return 0


def get_historical_item_rate(client: ERPNextClient, item_code: str, supplier: str = None) -> Tuple[float, int]:
    """
    Get historical average rate for an item from past purchase orders.
    
    Returns: (average_rate, count_of_orders)
    """
    try:
        pos = client.list_purchase_orders(limit=100)
        if not pos:
            return 0.0, 0
        
        matching_rates = []
        
        for po in pos:
            # Skip draft/cancelled orders
            if po.get('status') in ['Draft', 'Cancelled', 'Amended']:
                continue
            
            # Filter by supplier if provided
            if supplier and po.get('supplier') != supplier:
                continue
            
            # Look for the item in this PO
            if po.get('items'):
                for item in po['items']:
                    if item.get('item_code') == item_code:
                        rate = float(item.get('rate') or 0)
                        if rate > 0:
                            matching_rates.append(rate)
        
        if not matching_rates:
            return 0.0, 0
        
        avg_rate = sum(matching_rates) / len(matching_rates)
        return avg_rate, len(matching_rates)
    except:
        return 0.0, 0


def calculate_price_anomalies(client: ERPNextClient, po: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Check each item in PO for price anomalies.
    
    Returns list of anomalies: {item_code, rate, avg_rate, delta%, is_anomaly}
    """
    anomalies = []
    supplier = po.get('supplier', '')
    
    if not po.get('items'):
        return anomalies
    
    for item in po['items']:
        item_code = item.get('item_code')
        current_rate = float(item.get('rate') or 0)
        
        # Get historical average
        avg_rate, count = get_historical_item_rate(client, item_code, supplier)
        
        # Calculate delta
        if avg_rate > 0:
            delta_pct = ((current_rate - avg_rate) / avg_rate) * 100
            is_anomaly = delta_pct >= 20  # 20% above average = anomaly
        else:
            delta_pct = None
            is_anomaly = False  # Can't flag without baseline
        
        anomalies.append({
            'item_code': item_code,
            'item_name': item.get('item_name', item_code),
            'rate': current_rate,
            'avg_rate': avg_rate,
            'delta_pct': delta_pct,
            'is_anomaly': is_anomaly,
            'historical_count': count
        })
    
    return anomalies


def analyze_po_approval(po_name: str, client: ERPNextClient) -> Dict[str, Any]:
    """
    Main approval analyzer function.
    
    Returns: {decision, summary, findings, evidence, next_actions}
    """
    
    # Fetch PO details
    try:
        po = client.get_purchase_order(po_name)
    except Exception as e:
        return {
            'decision': 'REVIEW',
            'summary': f'Error fetching PO: {str(e)}',
            'findings': [f'Could not fetch PO details: {str(e)}'],
            'evidence': [],
            'next_actions': ['Verify PO name is correct', 'Check system connectivity']
        }
    
    if not po:
        return {
            'decision': 'REVIEW',
            'summary': f'PO {po_name} not found',
            'findings': ['PO does not exist in system'],
            'evidence': [],
            'next_actions': ['Verify PO name', 'Create PO if needed']
        }
    
    # Build summary
    supplier = po.get('supplier', 'Unknown')
    status = po.get('status', 'Unknown')
    total = float(po.get('grand_total', 0))
    items_count = len(po.get('items', []))
    date = po.get('transaction_date', 'N/A')
    
    summary = f"Supplier: {supplier} | Status: {status} | Total: {total:,.0f} ILS | Items: {items_count} | Date: {date}"
    
    # Analyze price anomalies
    anomalies = calculate_price_anomalies(client, po)
    anomaly_items = [a for a in anomalies if a['is_anomaly']]
    
    # Check supplier risk
    open_orders = get_supplier_open_orders(client, supplier)
    
    # Build findings
    findings = []
    risk_score = 0
    
    # Price anomalies
    if anomaly_items:
        findings.append(f"⚠️  Price anomalies detected: {len(anomaly_items)} item(s) >= 20% above average")
        risk_score += 30
    
    # Missing historical data
    missing_data_items = [a for a in anomalies if a['historical_count'] == 0]
    if missing_data_items:
        findings.append(f"❓ Insufficient historical data: {len(missing_data_items)} item(s) have no past purchase records")
        if not anomaly_items:
            risk_score += 10
    
    # Supplier open orders
    if open_orders >= 3:
        findings.append(f"⚠️  Supplier has {open_orders} open orders pending")
        risk_score += 15
    
    # Status checks
    if status not in ['Draft', 'To Receive']:
        findings.append(f"ℹ️  PO status is '{status}' (not standard for approval)")
    
    if not findings:
        findings.append("✅ No significant risks or anomalies detected")
    
    # Decision logic
    if anomaly_items and risk_score >= 30:
        decision = "DO NOT APPROVE"
        reason = "Price anomalies and/or high supplier risk"
    elif risk_score >= 25 or missing_data_items:
        decision = "REVIEW"
        reason = "Moderate risks or missing data require review"
    else:
        decision = "APPROVE"
        reason = "No significant risks detected"
    
    findings.insert(0, f"Decision: {decision} ({reason})")
    
    # Build evidence table
    evidence = []
    for anomaly in anomalies:
        evidence.append({
            'item_code': anomaly['item_code'],
            'rate': f"${anomaly['rate']:.2f}",
            'avg_rate': f"${anomaly['avg_rate']:.2f}" if anomaly['avg_rate'] > 0 else "N/A",
            'delta': f"{anomaly['delta_pct']:.1f}%" if anomaly['delta_pct'] is not None else "N/A",
            'status': "🚨 ANOMALY" if anomaly['is_anomaly'] else "✓"
        })
    
    # Next actions
    next_actions = []
    
    if anomaly_items:
        next_actions.append(
            f"Negotiate price on {len(anomaly_items)} item(s) to match historical average"
        )
    
    if missing_data_items:
        next_actions.append(
            f"Request quote or market price check for {len(missing_data_items)} item(s)"
        )
    
    if open_orders >= 3:
        next_actions.append(
            f"Confirm delivery dates on {open_orders} open orders before approving new orders"
        )
    
    if not next_actions:
        next_actions.append("Proceed with approval")
    
    return {
        'decision': decision,
        'summary': summary,
        'findings': findings,
        'evidence': evidence,
        'next_actions': next_actions,
        'risk_score': risk_score,
        'po_data': po
    }
