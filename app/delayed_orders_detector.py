"""Delayed Orders Detection for ERPNext Purchase Orders"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict


def detect_delayed_orders(purchase_orders: List[Dict]) -> Dict[str, Any]:
    """Detect and analyze delayed purchase orders."""
    if not purchase_orders:
        return {
            "delayed_orders": [],
            "summary": {
                "total_orders": 0,
                "delayed_count": 0,
                "on_time_count": 0,
                "on_time_percentage": 0.0,
                "total_delay_days": 0,
                "average_delay_days": 0.0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            },
            "supplier_performance": [],
            "recommendations": ["No purchase orders to analyze."],
        }

    # Analyze orders
    delayed = _identify_delayed_orders(purchase_orders)
    supplier_perf = _calculate_supplier_performance(purchase_orders, delayed)
    recommendations = _generate_recommendations(delayed, supplier_perf)

    # Calculate summary
    total_orders = len(purchase_orders)
    delayed_count = len(delayed)
    on_time_count = total_orders - delayed_count
    on_time_pct = (on_time_count / total_orders * 100) if total_orders > 0 else 0
    total_delay = sum(d["days_overdue"] for d in delayed)
    avg_delay = (total_delay / delayed_count) if delayed_count > 0 else 0

    severity_counts = defaultdict(int)
    for order in delayed:
        severity_counts[order["severity"]] += 1

    return {
        "delayed_orders": sorted(delayed, key=lambda x: x["days_overdue"], reverse=True)[:50],
        "summary": {
            "total_orders": total_orders,
            "delayed_count": delayed_count,
            "on_time_count": on_time_count,
            "on_time_percentage": round(on_time_pct, 1),
            "total_delay_days": total_delay,
            "average_delay_days": round(avg_delay, 1),
            "critical_count": severity_counts.get("Critical", 0),
            "high_count": severity_counts.get("High", 0),
            "medium_count": severity_counts.get("Medium", 0),
            "low_count": severity_counts.get("Low", 0),
        },
        "supplier_performance": supplier_perf[:10],
        "recommendations": recommendations,
    }


def _identify_delayed_orders(purchase_orders: List[Dict]) -> List[Dict]:
    """Identify orders that are delayed."""
    delayed = []
    today = datetime.now().date()

    for po in purchase_orders:
        schedule_date_str = po.get("schedule_date") or po.get("delivery_date")
        
        if not schedule_date_str:
            continue

        # Parse date
        try:
            if isinstance(schedule_date_str, str):
                schedule_date = datetime.strptime(schedule_date_str[:10], "%Y-%m-%d").date()
            else:
                schedule_date = schedule_date_str
        except (ValueError, TypeError):
            continue

        # Check if delayed
        if schedule_date < today:
            days_overdue = (today - schedule_date).days
            amount = _safe_float(po.get("grand_total")) or 0
            
            order_data = {
                "po_name": po.get("name", "Unknown"),
                "supplier": po.get("supplier_name") or po.get("supplier", "Unknown"),
                "schedule_date": str(schedule_date),
                "days_overdue": days_overdue,
                "amount": _format_currency(amount),
                "amount_raw": amount,
                "status": po.get("status", "Unknown"),
                "items_count": len(po.get("items", [])) if isinstance(po.get("items"), list) else 1,
                "severity": _classify_delay_severity(days_overdue),
            }
            
            delayed.append(order_data)

    return delayed


def _calculate_supplier_performance(
    purchase_orders: List[Dict],
    delayed_orders: List[Dict]
) -> List[Dict]:
    """Calculate on-time delivery performance by supplier."""
    supplier_stats = defaultdict(lambda: {"total": 0, "delayed": 0, "delay_days": []})

    # Count all orders by supplier
    for po in purchase_orders:
        supplier = po.get("supplier_name") or po.get("supplier", "Unknown")
        supplier_stats[supplier]["total"] += 1

    # Count delayed orders by supplier
    for delayed in delayed_orders:
        supplier = delayed["supplier"]
        supplier_stats[supplier]["delayed"] += 1
        supplier_stats[supplier]["delay_days"].append(delayed["days_overdue"])

    # Calculate metrics
    performance = []
    for supplier, stats in supplier_stats.items():
        total = stats["total"]
        delayed_count = stats["delayed"]
        on_time = total - delayed_count
        on_time_pct = (on_time / total * 100) if total > 0 else 100
        avg_delay = (sum(stats["delay_days"]) / len(stats["delay_days"])) if stats["delay_days"] else 0

        performance.append({
            "supplier": supplier,
            "total_orders": total,
            "on_time_orders": on_time,
            "delayed_orders": delayed_count,
            "on_time_percentage": round(on_time_pct, 1),
            "average_delay_days": round(avg_delay, 1),
            "performance_rating": _rate_supplier(on_time_pct),
        })

    # Sort by on-time percentage
    performance.sort(key=lambda x: x["on_time_percentage"])
    return performance


def _generate_recommendations(delayed: List[Dict], supplier_perf: List[Dict]) -> List[str]:
    """Generate actionable recommendations based on delayed orders."""
    if not delayed:
        return ["All orders are on schedule. Great job!"]

    recommendations = []

    # Critical delays
    critical = [d for d in delayed if d["severity"] == "Critical"]
    if critical:
        recommendations.append(
            f"🚨 {len(critical)} orders are severely delayed (60+ days). "
            f"Immediate escalation and supplier contact required."
        )

    # High delays
    high = [d for d in delayed if d["severity"] == "High"]
    if high:
        recommendations.append(
            f"⚠️ {len(high)} orders delayed 30-60 days. "
            f"Contact suppliers immediately and request expedited delivery."
        )

    # Supplier issues
    problematic = [s for s in supplier_perf if s["on_time_percentage"] < 50]
    if problematic:
        worst = problematic[0]
        recommendations.append(
            f"📋 Supplier '{worst['supplier']}' has only {worst['on_time_percentage']}% on-time delivery. "
            f"Consider renegotiating SLA or finding alternatives."
        )

    # Total impact
    total_delayed_amount = sum(d["amount_raw"] for d in delayed)
    if total_delayed_amount > 0:
        recommendations.append(
            f"💰 Total value of delayed orders: ${total_delayed_amount:,.2f}. "
            f"This impacts cash flow and operations."
        )

    # Process improvement
    avg_delay = sum(d["days_overdue"] for d in delayed) / len(delayed) if delayed else 0
    recommendations.append(
        f"📊 Average delay is {avg_delay:.0f} days. "
        f"Implement early warning system and improve supplier SLA enforcement."
    )

    return recommendations[:6]


def _classify_delay_severity(days_overdue: int) -> str:
    """Classify delay severity based on days overdue."""
    if days_overdue >= 60:
        return "Critical"
    elif days_overdue >= 30:
        return "High"
    elif days_overdue >= 15:
        return "Medium"
    else:
        return "Low"


def _rate_supplier(on_time_pct: float) -> str:
    """Rate supplier performance."""
    if on_time_pct >= 95:
        return "Excellent"
    elif on_time_pct >= 85:
        return "Good"
    elif on_time_pct >= 70:
        return "Fair"
    else:
        return "Poor"


def _safe_float(value: Any) -> float:
    """Safely convert value to float."""
    if value is None:
        return None
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None
    return None


def _format_currency(value: float) -> str:
    """Format value as currency."""
    if value is None or value == 0:
        return "$0.00"
    return f"${value:,.2f}"
