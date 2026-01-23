import re
from typing import Dict, Any


def parse_intent(text: str) -> Dict[str, Any]:
    """
    Very simple intent parser (MCP-style):
    - Understands suppliers/items/purchase orders
    - Can extract a Purchase Order name if the user typed it (e.g., PUR-ORD-2026-00001)
    - Can detect report generation requests
    - Can recognize PO approval requests
    """
    q = (text or "").strip().lower()

    # PO Approval - check FIRST (most specific)
    if "approve" in q or "should i approve" in q or "can i approve" in q:
        # Extract PO name if present (e.g., "Should I approve PUR-ORD-2026-00001?")
        m = re.search(r"(pur-ord-\d{4}-\d{5})", q)
        if m:
            return {"intent": "approve_po", "po_name": m.group(1).upper()}
        return {"intent": "approve_po"}

    # Price anomalies - check FIRST
    if "expensive" in q or "anomal" in q or "overpriced" in q or "unusual" in q:
        return {"intent": "detect_price_anomalies"}
    if "price" in q and ("check" in q or "anomal" in q or "unusual" in q):
        return {"intent": "detect_price_anomalies"}

    # Delayed orders
    if "delay" in q or "late" in q or "overdue" in q or "past due" in q:
        return {"intent": "detect_delayed_orders"}
    if ("slow" in q or "behind" in q) and ("delivery" in q or "order" in q):
        return {"intent": "detect_delayed_orders"}

    # Customer queries - HIGH PRIORITY (before sales/purchase)
    if "customer" in q:
        return {"intent": "list_customers"}

    # SALES ORDER - MUST check BEFORE generic "order" keyword
    if "sales order" in q or ("so" in q):
        return {"intent": "list_sales_orders"}

    # Invoice/Bill queries
    if "invoice" in q or "sales invoice" in q:
        return {"intent": "list_sales_invoices"}

    if "vendor bill" in q or ("bill" in q and "purchase" in q):
        return {"intent": "list_vendor_bills"}

    # Purchase Order by NAME (PUR-ORD-XXXX-XXXXX)
    m = re.search(r"(pur-ord-\d{4}-\d{5})", q)
    if m:
        return {"intent": "get_purchase_order", "po_name": m.group(1).upper()}

    # Report requests
    if "monthly" in q and ("report" in q or "spend" in q or "דוח" in q):
        return {"intent": "monthly_report"}

    if "pending" in q and ("report" in q or "order" in q):
        return {"intent": "pending_report"}

    if "spend report" in q or "דוח הוצאות" in q:
        return {"intent": "monthly_report"}

    # Item/Supplier (before generic order)
    if "item" in q or "מוצר" in q or "פריט" in q:
        return {"intent": "list_items"}

    if "supplier" in q or "ספק" in q:
        return {"intent": "list_suppliers"}

    # PURCHASE ORDER - generic "order" keyword (LAST, after all specific checks)
    if "purchase order" in q or "purchase" in q or "order" in q or "הזמנת רכש" in q or "רכש" in q:
        return {"intent": "list_purchase_orders"}

    if "total" in q or "sum" in q or "סהכ" in q or "סכום" in q:
        return {"intent": "total_spend"}

    return {"intent": "unknown"}
