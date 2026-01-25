"""
Purchase Order Risk Assessment Analyzer

Evaluates PO risk based on:
1. Order Status (Completed vs Pending)
2. Price Risk (anomalies, high amounts)
3. Supplier Risk (open orders, delays)
4. Data Completeness (missing receipts/invoices)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


def analyze_po_risks(pos: List[Dict], client=None) -> Dict[str, Any]:
    """
    Analyze all purchase orders and assign risk levels.
    
    Returns: {
        "summary": {...},
        "orders": [
            {
                "order_id": "PUR-ORD-2026-00001",
                "supplier": "Supplier Name",
                "status": "To Receive and Bill",
                "amount": 1000.00,
                "risk_level": "🟡 Medium Risk",
                "risk_score": 45,
                "reasons": ["...", "..."],
                "recommendation": "..."
            }
        ],
        "high_risk_count": 2,
        "medium_risk_count": 5,
        "low_risk_count": 10
    }
    """
    
    if not pos:
        return {
            "summary": "No purchase orders found.",
            "orders": [],
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }
    
    risk_assessments = []
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    
    # Analyze each PO
    for po in pos:
        assessment = evaluate_po_risk(po, pos, client)
        risk_assessments.append(assessment)
        
        if "🔴" in assessment["risk_level"]:
            high_risk_count += 1
        elif "🟡" in assessment["risk_level"]:
            medium_risk_count += 1
        else:
            low_risk_count += 1
    
    # Sort by risk score (highest first)
    risk_assessments.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "summary": f"Risk analysis: {high_risk_count} High, {medium_risk_count} Medium, {low_risk_count} Low",
        "orders": risk_assessments,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "recommendations": generate_recommendations(risk_assessments)
    }


def evaluate_po_risk(po: Dict, all_pos: List[Dict], client=None) -> Dict[str, Any]:
    """
    Evaluate risk for a single purchase order.
    
    Risk scoring:
    - Status: 0-40 points
    - Price: 0-30 points
    - Supplier: 0-20 points
    - Completeness: 0-10 points
    Total: 0-100 points
    """
    
    risk_score = 0
    reasons = []
    
    po_id = po.get("name", "Unknown")
    supplier = po.get("supplier", "Unknown")
    status = po.get("status", "Unknown")
    amount = float(po.get("grand_total", 0))
    transaction_date = po.get("transaction_date", "")
    
    # 1. STATUS RISK (0-40 points)
    status_score, status_reason = evaluate_status_risk(po, transaction_date)
    risk_score += status_score
    if status_reason:
        reasons.append(status_reason)
    
    # 2. PRICE RISK (0-30 points)
    price_score, price_reason = evaluate_price_risk(po, all_pos)
    risk_score += price_score
    if price_reason:
        reasons.append(price_reason)
    
    # 3. SUPPLIER RISK (0-20 points)
    supplier_score, supplier_reason = evaluate_supplier_risk(supplier, all_pos)
    risk_score += supplier_score
    if supplier_reason:
        reasons.append(supplier_reason)
    
    # 4. COMPLETENESS RISK (0-10 points)
    completeness_score, completeness_reason = evaluate_completeness_risk(po)
    risk_score += completeness_score
    if completeness_reason:
        reasons.append(completeness_reason)
    
    # Determine risk level
    if risk_score >= 60:
        risk_level = "🔴 High Risk"
    elif risk_score >= 30:
        risk_level = "🟡 Medium Risk"
    else:
        risk_level = "🟢 Low Risk"
    
    # Generate recommendation
    recommendation = generate_po_recommendation(risk_level, reasons)
    
    return {
        "order_id": po_id,
        "supplier": supplier,
        "status": status,
        "amount": amount,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "reasons": reasons,
        "recommendation": recommendation
    }


def evaluate_status_risk(po: Dict, transaction_date: str) -> tuple[int, str]:
    """
    Evaluate risk based on order status and age.
    
    Completed → 0 points (Low risk)
    To Receive/To Bill → 20 points (Medium risk)
    Long pending (>30 days) → 40 points (High risk)
    """
    
    status = po.get("status", "")
    
    if status == "Completed":
        return 0, ""
    
    if "To Receive" in status or "To Bill" in status:
        # Check how long it's been pending
        if transaction_date:
            try:
                po_date = datetime.fromisoformat(transaction_date.split()[0])
                days_pending = (datetime.now() - po_date).days
                
                if days_pending > 30:
                    return 40, f"Order pending for {days_pending} days (>30 days = High Risk)"
                elif days_pending > 14:
                    return 25, f"Order pending for {days_pending} days (>2 weeks)"
                else:
                    return 15, f"Order pending - awaiting receipt/invoice"
            except:
                return 20, "Status shows pending items"
        else:
            return 20, "Status shows pending items"
    
    if status == "Cancelled":
        return 5, "Order cancelled (low risk)"
    
    return 10, f"Status: {status}"


def evaluate_price_risk(po: Dict, all_pos: List[Dict]) -> tuple[int, str]:
    """
    Evaluate risk based on price compared to average.
    
    20%+ above average → 30 points (High risk)
    10-20% above average → 15 points (Medium risk)
    Within range → 0 points (Low risk)
    """
    
    amount = float(po.get("grand_total", 0))
    
    if amount == 0:
        return 5, "Order amount is zero"
    
    # Calculate average PO amount
    amounts = [float(p.get("grand_total", 0)) for p in all_pos if p.get("grand_total")]
    if not amounts or len(amounts) < 2:
        return 0, ""
    
    average = sum(amounts) / len(amounts)
    
    if average == 0:
        return 0, ""
    
    percentage_diff = ((amount - average) / average) * 100
    
    if percentage_diff >= 20:
        return 30, f"Order amount ${amount:,.2f} is {percentage_diff:.0f}% above average (${average:,.2f})"
    elif percentage_diff >= 10:
        return 15, f"Order amount ${amount:,.2f} is {percentage_diff:.0f}% above average"
    elif percentage_diff > 0:
        return 5, f"Order amount slightly above average"
    
    return 0, ""


def evaluate_supplier_risk(supplier: str, all_pos: List[Dict]) -> tuple[int, str]:
    """
    Evaluate risk based on supplier performance.
    
    3+ open orders from same supplier → 20 points
    1-2 open orders → 10 points
    Delayed orders history → 15 points
    Single order, on time → 0 points
    """
    
    # Count open orders from this supplier
    open_orders = [
        p for p in all_pos
        if p.get("supplier") == supplier and p.get("status") not in ["Completed", "Cancelled"]
    ]
    
    score = 0
    reason = ""
    
    if len(open_orders) >= 3:
        score = 20
        reason = f"Supplier has {len(open_orders)} open orders (concentration risk)"
    elif len(open_orders) >= 1:
        score = 10
        reason = f"Supplier has {len(open_orders)} open order(s)"
    
    # Check for delayed orders from this supplier
    delayed_orders = [
        p for p in all_pos
        if p.get("supplier") == supplier and "To Receive" in p.get("status", "") or "To Bill" in p.get("status", "")
    ]
    
    if len(delayed_orders) > len(open_orders):
        score = max(score, 15)
        reason = f"Supplier has pattern of pending orders"
    
    return score, reason


def evaluate_completeness_risk(po: Dict) -> tuple[int, str]:
    """
    Evaluate risk based on missing data.
    
    Missing receipts/invoices → 10 points
    Complete data → 0 points
    """
    
    status = po.get("status", "")
    
    # If To Receive, missing receipt
    if "To Receive" in status:
        return 8, "Awaiting goods receipt"
    
    # If To Bill, missing invoice
    if "To Bill" in status:
        return 8, "Awaiting supplier invoice"
    
    return 0, ""


def generate_po_recommendation(risk_level: str, reasons: List[str]) -> str:
    """Generate action recommendation based on risk level."""
    
    if "🔴" in risk_level:
        if any("delay" in r.lower() for r in reasons):
            return "Urgent: Contact supplier immediately about delivery delays"
        elif any("amount" in r.lower() or "above" in r.lower() for r in reasons):
            return "Action: Negotiate pricing or find alternative supplier"
        else:
            return "Action: Review order and take corrective action"
    
    elif "🟡" in risk_level:
        if any("pending" in r.lower() for r in reasons):
            return "Follow up: Check on order status with supplier"
        elif any("open" in r.lower() for r in reasons):
            return "Monitor: Track supplier performance on multiple orders"
        else:
            return "Review: Monitor this order closely"
    
    else:  # 🟢 Low Risk
        return "No action needed - order tracking normally"


def generate_recommendations(risk_assessments: List[Dict]) -> List[str]:
    """Generate top recommendations based on all risks."""
    
    recommendations = []
    
    high_risk = [o for o in risk_assessments if "🔴" in o["risk_level"]]
    medium_risk = [o for o in risk_assessments if "🟡" in o["risk_level"]]
    
    if high_risk:
        count = len(high_risk)
        recommendations.append(f"⚠️ {count} HIGH RISK order(s) require immediate attention")
        
        # Top high-risk orders
        for order in high_risk[:2]:
            recommendations.append(f"  • {order['order_id']} ({order['supplier']}): {order['recommendation']}")
    
    if medium_risk and len(medium_risk) > 3:
        recommendations.append(f"📊 {len(medium_risk)} medium risk orders - review supplier performance")
    
    if len(recommendations) == 0:
        recommendations.append("✅ All orders appear to be low risk - continue normal monitoring")
    
    return recommendations
