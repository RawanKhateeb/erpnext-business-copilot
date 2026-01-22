"""
Business Insights Layer for Purchase Orders

Analyzes purchase order data and generates actionable metrics and recommendations.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict


# ============================================================================
# FORMATTING HELPERS
# ============================================================================


def format_currency(amount: float) -> str:
    """Format amount as currency string.
    
    Args:
        amount: Numeric amount to format
        
    Returns:
        Formatted currency string (e.g., "$1,234.56")
    """
    try:
        value = float(amount) if amount is not None else 0.0
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_percentage(part: float, whole: float) -> str:
    """Calculate and format percentage.
    
    Args:
        part: Numerator
        whole: Denominator
        
    Returns:
        Formatted percentage string (e.g., "45.5%")
    """
    if whole == 0:
        return "0.0%"
    return f"{(part / whole * 100):.1f}%"


# ============================================================================
# INSIGHT COMPUTATION FUNCTIONS
# ============================================================================


def _safe_float(value: Any) -> float:
    """Safely convert value to float, default to 0.0."""
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def _extract_spend_by_supplier(
    purchase_orders: List[Dict[str, Any]]
) -> Dict[str, float]:
    """Extract and sum spend grouped by supplier.
    
    Args:
        purchase_orders: List of PO dicts
        
    Returns:
        Dict mapping supplier name to total spend
    """
    supplier_spend = defaultdict(float)
    for po in purchase_orders:
        supplier = po.get("supplier", "Unknown Supplier")
        amount = _safe_float(po.get("grand_total"))
        supplier_spend[supplier] += amount
    return dict(supplier_spend)


def _extract_counts_by_status(
    purchase_orders: List[Dict[str, Any]]
) -> Dict[str, int]:
    """Count POs by their status.
    
    Args:
        purchase_orders: List of PO dicts
        
    Returns:
        Dict mapping status to count
    """
    status_counts = defaultdict(int)
    for po in purchase_orders:
        status = po.get("status", "Unknown")
        status_counts[status] += 1
    return dict(status_counts)


def _get_top_suppliers(
    supplier_spend: Dict[str, float], limit: int = 3
) -> List[Tuple[str, float]]:
    """Get top suppliers by spend.
    
    Args:
        supplier_spend: Dict of supplier name -> total spend
        limit: Number of top suppliers to return
        
    Returns:
        List of (supplier_name, spend) tuples, sorted by spend descending
    """
    sorted_suppliers = sorted(
        supplier_spend.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return sorted_suppliers[:limit]


def _count_pending_orders(purchase_orders: List[Dict[str, Any]]) -> int:
    """Count orders that are pending (not completed or closed).
    
    Args:
        purchase_orders: List of PO dicts
        
    Returns:
        Number of pending orders
    """
    pending_statuses = {"Completed", "Closed", "Cancelled"}
    return sum(
        1 for po in purchase_orders
        if po.get("status", "").strip() not in pending_statuses
    )


# ============================================================================
# RECOMMENDATION GENERATION
# ============================================================================


def _generate_recommendations(
    total_orders: int,
    total_spend: float,
    pending_count: int,
    status_counts: Dict[str, int],
    supplier_spend: Dict[str, float],
    top_suppliers: List[Tuple[str, float]]
) -> List[str]:
    """Generate actionable recommendations based on PO data.
    
    Args:
        total_orders: Total number of orders
        total_spend: Sum of all grand_totals
        pending_count: Count of pending orders
        status_counts: Dict of status -> count
        supplier_spend: Dict of supplier -> spend
        top_suppliers: List of (supplier, spend) tuples
        
    Returns:
        List of recommendation strings (3-6 items)
    """
    recommendations = []

    # No orders
    if total_orders == 0:
        recommendations.append(
            "No purchase orders found. Create one to start tracking spend."
        )
        return recommendations

    # Pending orders
    if pending_count > 0:
        pct = format_percentage(pending_count, total_orders)
        recommendations.append(
            f"{pending_count} orders ({pct}) are pending. Review receiving/billing status."
        )

    # To Receive
    to_receive_count = status_counts.get("To Receive and Bill", 0) + \
                      status_counts.get("To Receive", 0)
    if to_receive_count > 3:
        recommendations.append(
            f"Many orders ({to_receive_count}) await receipt. Coordinate with warehouse/receiving team."
        )

    # To Bill
    to_bill_count = status_counts.get("To Bill", 0) + \
                   status_counts.get("To Receive and Bill", 0)
    if to_bill_count > 0:
        recommendations.append(
            f"{to_bill_count} orders need billing. Process invoices to keep accounts current."
        )

    # Supplier concentration
    if top_suppliers:
        top_spend = top_suppliers[0][1]
        if top_spend > total_spend * 0.5:
            top_supplier = top_suppliers[0][0]
            pct = format_percentage(top_spend, total_spend)
            recommendations.append(
                f"Supplier '{top_supplier}' accounts for {pct} of spend. "
                f"Consider diversifying to reduce dependency."
            )

    # Few suppliers
    if len(supplier_spend) <= 2 and len(supplier_spend) > 0:
        recommendations.append(
            "You work with very few suppliers. Consider diversifying for better negotiating power "
            "and resilience."
        )

    # Many suppliers
    if len(supplier_spend) > 10:
        recommendations.append(
            "You have many suppliers. Consolidating could improve margins and reduce complexity."
        )

    # High average order value
    avg_order = total_spend / total_orders if total_orders > 0 else 0
    if avg_order > 10000:
        recommendations.append(
            f"Average order value is {format_currency(avg_order)}. "
            f"Consider reviewing large orders for cost optimization."
        )

    return recommendations[:6]  # Limit to 6 recommendations


# ============================================================================
# MAIN INSIGHTS FUNCTION
# ============================================================================


def build_purchase_order_insights(
    purchase_orders: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build comprehensive business insights from purchase order data.
    
    Computes metrics including:
    - Total orders and spend
    - Status breakdown
    - Top suppliers
    - Pending order count
    - Actionable recommendations
    
    Args:
        purchase_orders: List of purchase order dicts from ERPNext
        
    Returns:
        Dict containing:
        {
            "total_orders": int,
            "total_spend": float,
            "total_spend_formatted": str,
            "counts_by_status": dict,
            "top_suppliers_by_spend": list[tuple],
            "pending_orders_count": int,
            "supplier_count": int,
            "average_order_value": float,
            "average_order_value_formatted": str,
            "recommendations": list[str],
        }
        
    Example:
        >>> pos = [
        ...     {"grand_total": 500, "status": "Completed", "supplier": "Supplier A"},
        ...     {"grand_total": 750, "status": "Pending", "supplier": "Supplier B"},
        ... ]
        >>> insights = build_purchase_order_insights(pos)
        >>> insights["total_spend"]
        1250.0
    """
    # Handle empty list
    if not purchase_orders:
        return {
            "total_orders": 0,
            "total_spend": 0.0,
            "total_spend_formatted": "$0.00",
            "counts_by_status": {},
            "top_suppliers_by_spend": [],
            "pending_orders_count": 0,
            "supplier_count": 0,
            "average_order_value": 0.0,
            "average_order_value_formatted": "$0.00",
            "recommendations": [
                "No purchase orders found. Create one to start tracking spend."
            ],
        }

    # Compute basic metrics
    total_orders = len(purchase_orders)
    total_spend = sum(_safe_float(po.get("grand_total")) for po in purchase_orders)
    average_order_value = total_spend / total_orders if total_orders > 0 else 0.0

    # Compute derived metrics
    supplier_spend = _extract_spend_by_supplier(purchase_orders)
    status_counts = _extract_counts_by_status(purchase_orders)
    top_suppliers = _get_top_suppliers(supplier_spend, limit=3)
    pending_count = _count_pending_orders(purchase_orders)

    # Generate recommendations
    recommendations = _generate_recommendations(
        total_orders=total_orders,
        total_spend=total_spend,
        pending_count=pending_count,
        status_counts=status_counts,
        supplier_spend=supplier_spend,
        top_suppliers=top_suppliers,
    )

    return {
        "total_orders": total_orders,
        "total_spend": total_spend,
        "total_spend_formatted": format_currency(total_spend),
        "counts_by_status": status_counts,
        "top_suppliers_by_spend": [
            {"name": name, "spend": amount, "spend_formatted": format_currency(amount)}
            for name, amount in top_suppliers
        ],
        "pending_orders_count": pending_count,
        "supplier_count": len(supplier_spend),
        "average_order_value": average_order_value,
        "average_order_value_formatted": format_currency(average_order_value),
        "recommendations": recommendations,
    }
