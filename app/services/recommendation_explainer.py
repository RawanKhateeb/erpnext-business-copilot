"""
Recommendation explanation generator

Explains each recommendation with evidence from actual data.
Uses ONLY data provided - never invents numbers or facts.
"""

from typing import Dict, List, Any


def explain_recommendations(intent: str, user_question: str, data: Dict[str, Any], 
                           insights: List[str], recommendations: List[str]) -> Dict[str, Any]:
    """
    Generate explanation for recommendations using only actual data.
    
    Args:
        intent: The detected intent (e.g., 'total_spend', 'list_purchase_orders')
        user_question: Original user question
        data: JSON data from ERPNext API
        insights: Generated insights
        recommendations: Generated recommendations
    
    Returns:
        {
            "title": "Why these recommendations?",
            "summary": "...",
            "reasons": [
                {"recommendation": "...", "evidence": "..."},
                ...
            ],
            "next_actions": ["...", "..."]
        }
    """
    
    explanation = {
        "title": "Why these recommendations?",
        "summary": "",
        "reasons": [],
        "next_actions": []
    }
    
    # TOTAL SPEND ANALYSIS
    if intent == "total_spend":
        total_spend = data.get('total_spend', 0)
        po_count = data.get('po_count', 0)
        completed_count = data.get('completed_count', 0)
        avg_order_value = data.get('average_order_value', 0)
        
        explanation["summary"] = f"Your organization has spent ${total_spend:,.2f} across {po_count} purchase orders, with an average order value of ${avg_order_value:,.2f}."
        
        # Reason 1: Total spend amount
        explanation["reasons"].append({
            "recommendation": "Total spend across all purchase orders",
            "evidence": f"${total_spend:,.2f} spent across {po_count} orders"
        })
        
        # Reason 2: Order completion rate
        completion_rate = (completed_count / po_count * 100) if po_count > 0 else 0
        explanation["reasons"].append({
            "recommendation": f"Order completion status: {completed_count} of {po_count} orders completed",
            "evidence": f"{completion_rate:.1f}% completion rate ({completed_count} completed, {po_count - completed_count} pending)"
        })
        
        # Reason 3: Average order value
        explanation["reasons"].append({
            "recommendation": "Average purchase order size indicates spending patterns",
            "evidence": f"Average order value: ${avg_order_value:,.2f} ({total_spend:,.2f} ÷ {po_count} orders)"
        })
        
        # Next actions
        explanation["next_actions"] = [
            f"Review pending orders ({po_count - completed_count}) to track delivery and invoicing progress",
            "Analyze spending trends by supplier to identify cost optimization opportunities",
            "Compare current spend to budget allocation for procurement planning"
        ]
    
    # LIST PURCHASE ORDERS
    elif intent == "list_purchase_orders":
        po_list = data if isinstance(data, list) else []
        po_count = len(po_list)
        
        explanation["summary"] = f"You have {po_count} purchase orders in the system with varying statuses and suppliers."
        
        # Reason 1: Total orders
        explanation["reasons"].append({
            "recommendation": "Total number of purchase orders",
            "evidence": f"{po_count} purchase orders found in the system"
        })
        
        # Reason 2: Status breakdown (if available)
        if po_count > 0 and any(po.get('status') for po in po_list):
            statuses = {}
            for po in po_list:
                status = po.get('status', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
            
            status_text = ", ".join([f"{count} {status}" for status, count in sorted(statuses.items())])
            explanation["reasons"].append({
                "recommendation": "Order status distribution",
                "evidence": f"{status_text}"
            })
        
        # Reason 3: Supplier diversity (if available)
        if po_count > 0 and any(po.get('supplier') for po in po_list):
            suppliers = set(po.get('supplier') for po in po_list if po.get('supplier'))
            explanation["reasons"].append({
                "recommendation": "Supplier diversity",
                "evidence": f"Orders placed with {len(suppliers)} different suppliers"
            })
        
        explanation["next_actions"] = [
            "Review orders by status (To Receive, To Bill, Completed) to track progress",
            "Analyze supplier concentration - ensure you're not over-dependent on single suppliers",
            f"Follow up on pending items in {po_count - sum(1 for po in po_list if po.get('status') == 'Completed')} orders"
        ]
    
    # PRICE ANOMALIES
    elif intent == "detect_price_anomalies":
        explanation["summary"] = "Price analysis identified items with unusual pricing compared to historical averages."
        
        anomalies = [item for item in (data if isinstance(data, list) else []) 
                    if item.get('is_anomaly')]
        normal_items = [item for item in (data if isinstance(data, list) else []) 
                       if not item.get('is_anomaly')]
        
        if anomalies:
            explanation["reasons"].append({
                "recommendation": f"Price anomalies detected in {len(anomalies)} item(s)",
                "evidence": f"Items priced {20}% or higher above historical average: {', '.join(a.get('item_code') for a in anomalies)}"
            })
        
        if normal_items:
            explanation["reasons"].append({
                "recommendation": f"Normal pricing confirmed for {len(normal_items)} item(s)",
                "evidence": f"Items within expected price range based on historical data"
            })
        
        if anomalies:
            explanation["next_actions"] = [
                f"Negotiate pricing on {len(anomalies)} item(s) to match historical averages",
                "Request quotes from alternative suppliers for high-priced items",
                "Verify if price increases are justified by market conditions or supplier communication"
            ]
        else:
            explanation["next_actions"] = [
                "Continue monitoring supplier pricing for consistency",
                "Maintain current suppliers if pricing remains competitive"
            ]
    
    # DELAYED ORDERS
    elif intent == "detect_delayed_orders":
        explanation["summary"] = "Analysis shows which orders are delayed and by how long."
        
        delayed = [item for item in (data if isinstance(data, list) else []) 
                  if item.get('is_delayed')]
        
        if delayed:
            total_days_late = sum(item.get('days_overdue', 0) for item in delayed)
            avg_days_late = total_days_late / len(delayed) if delayed else 0
            
            explanation["reasons"].append({
                "recommendation": f"{len(delayed)} order(s) are delayed",
                "evidence": f"Total {total_days_late} days overdue, averaging {avg_days_late:.1f} days late per order"
            })
            
            explanation["next_actions"] = [
                f"Follow up with suppliers on {len(delayed)} delayed order(s)",
                "Assess impact on production/operations due to delays",
                "Consider penalty clauses or supplier performance reviews if delays are recurring"
            ]
        else:
            explanation["summary"] = "No delayed orders detected - all deliveries on track."
            explanation["next_actions"] = [
                "Continue monitoring delivery schedules",
                "Maintain positive relationships with suppliers"
            ]
    
    # CUSTOMERS/SUPPLIERS/ITEMS LISTS
    elif intent in ["list_customers", "list_suppliers", "list_items", "list_sales_orders", "list_sales_invoices", "list_vendor_bills"]:
        item_type = intent.replace("list_", "").replace("_invoices", "").replace("_bills", "")
        count = len(data) if isinstance(data, list) else 0
        
        intent_names = {
            "customers": "customers",
            "suppliers": "suppliers", 
            "items": "items in catalog",
            "sales_orders": "sales orders",
            "sales": "sales invoices",
            "vendor": "vendor bills"
        }
        
        display_name = intent_names.get(item_type.replace("sales_order", "sales_orders"), item_type)
        
        explanation["summary"] = f"You have {count} {display_name} in the system."
        
        explanation["reasons"].append({
            "recommendation": f"Total {display_name} count",
            "evidence": f"{count} {display_name} found"
        })
        
        if isinstance(data, list) and count > 0:
            # Get unique values if applicable
            if 'supplier' in str(data[0]) or 'customer' in str(data[0]):
                unique_field = 'supplier' if 'supplier' in str(data[0]) else 'customer'
                unique_count = len(set(item.get(unique_field) for item in data if item.get(unique_field)))
                explanation["reasons"].append({
                    "recommendation": f"Unique {unique_field}s",
                    "evidence": f"{unique_count} different {unique_field}s involved"
                })
        
        explanation["next_actions"] = [
            f"Review {display_name} to identify inactive or high-value partners",
            f"Analyze performance metrics (spend, delivery, quality) for top {display_name}",
            f"Plan relationship management strategy for key {display_name}"
        ]
    
    return explanation


def format_explanation_text(explanation: Dict[str, Any]) -> str:
    """Format explanation as readable text."""
    
    text = f"\n{explanation['title']}\n"
    text += "=" * 50 + "\n\n"
    
    text += f"Summary:\n{explanation['summary']}\n\n"
    
    if explanation['reasons']:
        text += "Reasons:\n"
        for i, reason in enumerate(explanation['reasons'], 1):
            text += f"{i}. {reason['recommendation']}\n"
            text += f"   Evidence: {reason['evidence']}\n\n"
    
    if explanation['next_actions']:
        text += "Next Actions:\n"
        for action in explanation['next_actions']:
            text += f"• {action}\n"
    
    return text
