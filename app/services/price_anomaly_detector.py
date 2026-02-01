from typing import List, Dict, Any
from collections import defaultdict


def detect_price_anomalies(purchase_orders: List[Dict]) -> Dict[str, Any]:
    """Detect price anomalies in purchase orders."""
    if not purchase_orders:
        return {
            "anomalies": [],
            "summary": {"total_items_analyzed": 0, "items_with_anomalies": 0, "anomaly_count": 0},
            "recommendations": ["No purchase orders to analyze."],
        }

    item_purchases = _group_by_item(purchase_orders)
    item_metrics = _calculate_item_metrics(item_purchases)
    anomalies = _detect_anomalies(item_metrics, threshold=0.20)
    recommendations = _generate_anomaly_recommendations(anomalies, item_metrics)

    return {
        "anomalies": anomalies,
        "summary": {
            "total_items_analyzed": len(item_metrics),
            "items_with_anomalies": len(set(a["item_name"] for a in anomalies)),
            "anomaly_count": len(anomalies),
        },
        "recommendations": recommendations,
    }


def _group_by_item(purchase_orders: List[Dict]) -> Dict[str, List[Dict]]:
    """Group purchases by item name."""
    items = defaultdict(list)

    for po in purchase_orders:
        item_name = po.get("item_code") or po.get("item_name") or "Unknown"
        supplier = po.get("supplier") or po.get("supplier_name") or "Unknown"
        quantity = _safe_float(po.get("qty")) or _safe_float(po.get("quantity"))
        rate = _safe_float(po.get("rate")) or _safe_float(po.get("unit_price"))
        amount = _safe_float(po.get("amount")) or _safe_float(po.get("line_total"))

        if rate is None and quantity and amount:
            rate = amount / quantity
        elif rate is None:
            rate = amount

        if item_name and supplier and rate is not None:
            items[item_name].append({
                "supplier": supplier,
                "rate": rate,
                "quantity": quantity or 1,
                "amount": amount or (rate * (quantity or 1)),
                "status": po.get("status", "Unknown"),
            })

    return items


def _calculate_item_metrics(item_purchases: Dict[str, List[Dict]]) -> Dict[str, Dict[str, Any]]:
    """Calculate average price per item."""
    metrics = {}

    for item_name, purchases in item_purchases.items():
        if not purchases:
            continue

        rates = [p["rate"] for p in purchases]
        avg_rate = sum(rates) / len(rates)

        metrics[item_name] = {
            "average_rate": avg_rate,
            "min_rate": min(rates),
            "max_rate": max(rates),
            "supplier_count": len(set(p["supplier"] for p in purchases)),
            "purchases": purchases,
        }

    return metrics


def _detect_anomalies(item_metrics: Dict[str, Dict], threshold: float = 0.20) -> List[Dict]:
    """Detect prices 20% higher than average."""
    anomalies = []

    for item_name, metrics in item_metrics.items():
        avg_rate = metrics["average_rate"]
        threshold_price = avg_rate * (1 + threshold)

        for purchase in metrics["purchases"]:
            rate = purchase["rate"]

            if rate > threshold_price:
                difference = rate - avg_rate
                percentage = (difference / avg_rate) * 100 if avg_rate else 0

                anomalies.append({
                    "item_name": item_name,
                    "supplier": purchase["supplier"],
                    "price": _format_currency(rate),
                    "price_raw": rate,
                    "average_price": _format_currency(avg_rate),
                    "average_price_raw": avg_rate,
                    "difference": _format_currency(difference),
                    "difference_raw": difference,
                    "percentage": f"{percentage:.1f}%",
                    "percentage_raw": percentage,
                    "severity": _classify_severity(percentage),
                })

    anomalies.sort(key=lambda x: x["percentage_raw"], reverse=True)
    return anomalies


def _generate_anomaly_recommendations(anomalies: List[Dict], item_metrics: Dict[str, Dict]) -> List[str]:
    """Generate recommendations based on anomalies."""
    if not anomalies:
        return ["No significant price anomalies were detected."]

    recommendations = []
    critical = [a for a in anomalies if a["severity"] == "Critical"]
    high = [a for a in anomalies if a["severity"] == "High"]

    if critical:
        suppliers = set(a["supplier"] for a in critical)
        items = set(a["item_name"] for a in critical)
        recommendations.append(
            f"CRITICAL: {len(critical)} severe price anomalies. Negotiate with {', '.join(list(suppliers)[:2])} for {len(items)} items."
        )

    if high:
        recommendations.append(
            f"Review pricing from {len(set(a['supplier'] for a in high))} suppliers with prices {high[0]['percentage']} above average."
        )

    supplier_anomaly_count = defaultdict(int)
    for anomaly in anomalies:
        supplier_anomaly_count[anomaly["supplier"]] += 1

    top_offenders = sorted(supplier_anomaly_count.items(), key=lambda x: x[1], reverse=True)
    if top_offenders and top_offenders[0][1] > 1:
        recommendations.append(
            f"Supplier '{top_offenders[0][0]}' has {top_offenders[0][1]} price anomalies. Request quotes from competitors."
        )

    cheapest_suppliers = defaultdict(list)
    for item_name, metrics in item_metrics.items():
        min_supplier = min(metrics["purchases"], key=lambda x: x["rate"])
        cheapest_suppliers[min_supplier["supplier"]].append(item_name)

    if cheapest_suppliers:
        best_supplier = max(cheapest_suppliers.items(), key=lambda x: len(x[1]))
        recommendations.append(
            f"'{best_supplier[0]}' offers competitive pricing on {len(best_supplier[1])} items."
        )

    return recommendations[:4]


def _classify_severity(percentage: float) -> str:
    """Classify anomaly severity."""
    if percentage >= 50:
        return "Critical"
    elif percentage >= 30:
        return "High"
    elif percentage >= 20:
        return "Medium"
    return "Low"


def _safe_float(value: Any) -> float | None:
    """Safely convert to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None
    return None


def _format_currency(amount: float | None) -> str:
    """Format as currency."""
    if amount is None:
        return "$0.00"
    return f"${amount:,.2f}"
