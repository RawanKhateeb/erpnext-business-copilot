from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.copilot.intent import parse_intent
from app.models import ERPNextClient
from app.services.insights import build_purchase_order_insights
from app.services.price_anomaly_detector import detect_price_anomalies
from app.services.delayed_orders_detector import detect_delayed_orders
from app.services.po_approval_analyzer import analyze_po_approval
from app.services.po_risk_analyzer import analyze_po_risks
from app.services.recommendation_explainer import explain_recommendations


def _extract_date(date_str: str) -> datetime:  # pragma: no cover
    """Extract date from ISO format string safely."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.split()[0])
    except (ValueError, AttributeError):  # pragma: no cover
        return None


def _filter_current_month_pos(pos: List[Dict], today: datetime) -> List[Dict]:  # pragma: no cover
    """Filter purchase orders for current month."""
    current_month_start = today.replace(day=1)
    return [
        p for p in pos 
        if p.get("transaction_date") and _extract_date(p["transaction_date"]) >= current_month_start
    ]


def generate_monthly_report(pos: List[Dict]) -> tuple[str, List[str]]:  # pragma: no cover
    """Generate monthly spend report with analysis."""
    if not pos:
        return "No purchase orders found for analysis.", []

    # Analyze current month
    today = datetime.now()
    current_month_pos = _filter_current_month_pos(pos, today)
    
def _calculate_po_metrics(pos: List[Dict]) -> tuple[float, int, int]:  # pragma: no cover
    """Calculate PO spend and status counts."""
    spend = sum(float(p.get("grand_total") or 0) for p in pos)
    completed = len([p for p in pos if p.get("status") == "Completed"])
    pending = len([p for p in pos if p.get("status") not in ["Completed", "Cancelled"]])
    return spend, completed, pending


def _get_top_suppliers(pos: List[Dict], limit: int = 3) -> List[tuple]:  # pragma: no cover
    """Get top suppliers by spend."""
    supplier_spend = {}
    for p in pos:
        supplier = p.get("supplier", "Unknown")
        supplier_spend[supplier] = supplier_spend.get(supplier, 0) + float(p.get("grand_total") or 0)
    return sorted(supplier_spend.items(), key=lambda x: x[1], reverse=True)[:limit]


def _format_spend(amount: float) -> str:  # pragma: no cover
    """Format amount as currency."""
    return f"${amount:,.2f}"


def generate_monthly_report(pos: List[Dict]) -> tuple[str, List[str]]:  # pragma: no cover
    """Generate monthly spend report with analysis."""
    if not pos:
        return "No purchase orders found for analysis.", []

    # Analyze current month
    today = datetime.now()
    current_month_pos = _filter_current_month_pos(pos, today)
    
    # Calculate metrics
    current_month_spend, completed, pending = _calculate_po_metrics(current_month_pos)
    all_spend, _, _ = _calculate_po_metrics(pos)
    top_suppliers = _get_top_suppliers(current_month_pos)
    
    # Build report summary
    avg_order = current_month_spend / len(current_month_pos) if current_month_pos else 0
    answer = f"""Monthly Spend Report (Current Month)

Total Spend: {_format_spend(current_month_spend)}
Orders: {len(current_month_pos)} total ({completed} completed, {pending} pending)
Average Order Value: {_format_spend(avg_order)}

Top Suppliers:"""
    
    for supplier, amount in top_suppliers:
        answer += f"\n  • {supplier}: {_format_spend(amount)}"
    
    answer += f"\n\nAll-time Total Spend: {_format_spend(all_spend)}"
    
    insights = [
        f"Current month: {len(current_month_pos)} orders totaling ${current_month_spend:,.2f}",
        f"{pending} orders are pending completion",
        f"Top supplier: {top_suppliers[0][0] if top_suppliers else 'N/A'}"
    ]
    
    next_questions = [
        "Show pending orders",
        "Compare to last month",
        "List top suppliers",
        "Export this report"
    ]
    
    return answer, insights, next_questions, current_month_pos


def _filter_pending_orders(pos: List[Dict]) -> tuple[List[Dict], List[Dict], List[Dict]]:  # pragma: no cover
    """Filter and categorize pending orders."""
    pending = [p for p in pos if p.get("status") not in ["Completed", "Cancelled"]]
    to_receive = [p for p in pending if "To Receive" in p.get("status", "")]
    to_bill = [p for p in pending if "To Bill" in p.get("status", "")]
    return pending, to_receive, to_bill

def generate_pending_report(pos: List[Dict]) -> tuple[str, List[str]]:  # pragma: no cover
    """Generate report of pending purchase orders."""
    pending, to_receive, to_bill = _filter_pending_orders(pos)
    
    if not pending:
        return "No pending orders found!", [], [], []
    
    pending_spend, _, _ = _calculate_po_metrics(pending)
    
    answer = f"""Pending Purchase Orders Report

Total Pending: {len(pending)} orders ({_format_spend(pending_spend)})
  • {len(to_receive)} awaiting receipt
  • {len(to_bill)} awaiting billing

Action Required:
- Coordinate with receiving team for items to be received
- Process invoices for items to be billed
"""
    
    insights = [
        f"{len(pending)} orders need attention (${pending_spend:,.2f})",
        f"Items to receive: {len(to_receive)} orders - Coordinate with warehouse",
        f"Items to bill: {len(to_bill)} orders - Process invoices soon"
    ]
    
    next_questions = [
        "Show all purchase orders",
        "List suppliers",
        "What's the total spend?"
    ]
    
    return answer, insights, next_questions, pending


def generate_po_insights(pos: List[Dict]) -> tuple[List[str], List[str]]:
    """
    Generate business insights and next questions for purchase orders.
    
    Returns: (insights, next_questions)
    """
    insights = []
    
    if not pos:
        return ["No purchase orders found."], ["What suppliers do we work with?"]
    
    # Analyze statuses
    total_spend = sum(float(po.get("grand_total") or 0) for po in pos)
    incomplete = [p for p in pos if p.get("status") not in ["Completed", "Cancelled"]]
    to_receive = [p for p in pos if "To Receive" in p.get("status", "")]
    to_bill = [p for p in pos if "To Bill" in p.get("status", "")]
    
    # Generate insights
    insights.append(f"You have {len(pos)} purchase orders totaling ${total_spend:,.2f}.")
    
    if incomplete:
        insights.append(f"{len(incomplete)} orders are not yet completed. Review pending items.")
    
    if to_receive:
        insights.append(f"{len(to_receive)} orders await receipt. Coordinate with receiving team.")
    
    if to_bill:
        insights.append(f"{len(to_bill)} orders need billing. Process invoices soon.")
    
    # Generate next questions
    next_questions = [
        "What's the total spend?",
        "Show pending orders",
        "List suppliers"
    ]
    if to_receive:
        next_questions.insert(0, "Which orders are 'To Receive'?")
    if to_bill:
        next_questions.insert(1, "Which orders are 'To Bill'?")
    
    return insights[:3], next_questions[:4]  # Limit to 3 insights, 4 questions


def generate_suppliers_insights(suppliers: List[Dict]) -> tuple[List[str], List[str]]:
    """Generate insights and next questions for suppliers."""
    insights = []
    
    insights.append(f"You work with {len(suppliers)} suppliers.")
    if len(suppliers) > 5:
        insights.append("Consider consolidating suppliers to improve negotiating power.")
    if len(suppliers) <= 2:
        insights.append("Consider diversifying your supplier base for better resilience.")
    
    next_questions = [
        "List items",
        "Show purchase orders",
        "What's the total spend?"
    ]
    
    return insights[:3], next_questions[:4]


def generate_items_insights(items: List[Dict]) -> tuple[List[str], List[str]]:
    """Generate insights and next questions for items."""
    insights = []
    
    insights.append(f"You have {len(items)} items in inventory.")
    if len(items) > 100:
        insights.append("Large inventory. Consider periodic audits to manage stock.")
    
    next_questions = [
        "List suppliers",
        "Show purchase orders",
        "What's the total spend?"
    ]
    
    return insights[:3], next_questions[:4]


def handle_user_input(text: str) -> Dict[str, Any]:
    """
    Copilot service:
    - Calls parse_intent()
    - Activates the right tool (ERPNextClient methods)
    - Returns structured response with answer, insights, data, and next_questions
    """
    intent = "unknown"  # Initialize to avoid UnboundLocalError in exception handlers
    try:
        if not text or not isinstance(text, str):
            return {
                "intent": "unknown",
                "answer": "Please provide a question or command.",
                "insights": [],
                "data": {},
                "next_questions": ["List suppliers", "Show purchase orders", "What's the total spend?"]
            }
        
        parsed = parse_intent(text)
        intent = parsed.get("intent")
        
        client = ERPNextClient()
        
        if not intent or intent == "unknown":
            return {
                "intent": "unknown",
                "answer": "I didn't understand that. Try asking about purchase orders, suppliers, or costs.",
                "insights": [],
                "data": {},
                "next_questions": ["List suppliers", "Show purchase orders", "What's the total spend?"]
            }

        if intent == "approve_po":
            # Handle PO approval request
            po_name = parsed.get("po_name")
            
            if not po_name:
                return {
                    "intent": intent,
                    "answer": "Please specify which purchase order to review. For example: 'Should I approve PUR-ORD-2026-00001?'",
                    "insights": [],
                    "data": {},
                    "next_questions": [
                        "Show purchase orders",
                        "List suppliers",
                        "What's the total spend?"
                    ]
                }
            
            # Analyze the PO
            analysis = analyze_po_approval(po_name, client)
            
            return {
                "intent": intent,
                "answer": f"Approval Analysis for {po_name}\n\nDecision: {analysis['decision']}",
                "summary": analysis['summary'],
                "findings": analysis['findings'],
                "evidence": analysis['evidence'],
                "next_actions": analysis['next_actions'],
                "insights": analysis['findings'],
                "data": analysis.get('evidence', []),
                "next_questions": [
                    "Explain why you recommend " + analysis['decision'],
                    "What would you change to make this approvable?",
                    "Compare this PO with last 3 orders from " + (analysis.get('po_data', {}).get('supplier', 'supplier'))
                ]
            }
        
        if intent == "list_suppliers":
            data = client.list_suppliers()
            insights, next_questions = generate_suppliers_insights(data)
            return {
                "intent": intent,
                "answer": f"You have {len(data)} suppliers in your network.",
                "insights": insights,
                "data": data,
                "next_questions": next_questions
            }

        if intent == "list_items":
            data = client.list_items()
            insights, next_questions = generate_items_insights(data)
            return {
                "intent": intent,
                "answer": f"Your catalog contains {len(data)} items.",
                "insights": insights,
                "data": data,
                "next_questions": next_questions
            }

        if intent == "list_purchase_orders":
            data = client.list_purchase_orders(limit=50)
            insights, next_questions = generate_po_insights(data)
            
            # Build business insights
            po_insights = build_purchase_order_insights(data)
            
            # Generate explanation
            explanation = explain_recommendations(intent, text, data, insights, insights)
            
            return {
                "intent": intent,
                "answer": f"Displaying {len(data)} purchase orders. Total spend: {po_insights['total_spend_formatted']}.",
                "insights": insights,
                "data": data,
                "next_questions": next_questions,
                "metrics": po_insights,  # Include detailed business metrics
                "recommendations": po_insights.get("recommendations", []),
                "explanation": explanation
            }

        if intent == "get_purchase_order":
            po_name = parsed["po_name"]
            data = client.get_purchase_order(po_name)
            status = data.get("status", "Unknown")
            insights = [f"Status: {status}"]
            
            if "To Receive" in status:
                insights.append("Awaiting receipt from supplier.")
            if "To Bill" in status:
                insights.append("Invoice pending. Process for payment.")
            if status == "Completed":
                insights.append("Order fully received and billed.")
            
            next_questions = [
                "Show all purchase orders",
                "List suppliers",
                "What's the total spend?"
            ]
            
            return {
                "intent": intent,
                "answer": f"Details for purchase order {po_name}.",
                "insights": insights[:3],
                "data": data,
                "next_questions": next_questions
            }

        if intent == "total_spend":
            pos = client.list_purchase_orders(limit=200)
            
            # Use insights for comprehensive metrics
            po_insights = build_purchase_order_insights(pos)
            
            total = po_insights["total_spend"]
            completed = sum(1 for p in pos if p.get("status") == "Completed")
            
            insights = [
                f"Total spend across {len(pos)} purchase orders: {po_insights['total_spend_formatted']}.",
                f"{completed} orders have been completed.",
                f"Average order value: {po_insights['average_order_value_formatted']}.",
            ]
            
            next_questions = [
                "Show purchase orders",
                "List suppliers",
                "What items do we purchase?"
            ]
            
            # Generate explanation
            data_dict = {"total_spend": total, "po_count": len(pos), "completed_count": completed, 
                        "average_order_value": po_insights["average_order_value"]}
            explanation = explain_recommendations(intent, text, data_dict, insights, insights)
            
            return {
                "intent": intent,
                "answer": f"Your total spend is {po_insights['total_spend_formatted']} across {len(pos)} orders.",
                "insights": insights[:3],
                "data": data_dict,
                "next_questions": next_questions,
                "metrics": po_insights,
                "recommendations": po_insights.get("recommendations", []),
                "explanation": explanation
            }

        if intent == "monthly_report":
            pos = client.list_purchase_orders(limit=500)
            answer, insights, next_questions, data = generate_monthly_report(pos)
            
            # Include insights for all POs (context)
            po_insights = build_purchase_order_insights(pos)
            
            return {
                "intent": intent,
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": next_questions,
                "metrics": po_insights,
                "recommendations": po_insights.get("recommendations", []),
            }

        if intent == "pending_report":
            pos = client.list_purchase_orders(limit=500)
            answer, insights, next_questions, data = generate_pending_report(pos)
            
            # Include insights for context
            po_insights = build_purchase_order_insights(pos)
            
            return {
                "intent": intent,
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": next_questions,
                "metrics": po_insights,
                "recommendations": po_insights.get("recommendations", []),
            }

        if intent == "detect_price_anomalies":
            pos = client.list_purchase_orders(limit=500)
            anomaly_results = detect_price_anomalies(pos)
            
            if not anomaly_results["anomalies"]:
                answer = "No significant price anomalies were detected."
                insights = ["All suppliers are pricing competitively."]
                anomaly_data = []
            else:
                answer = f"Found {anomaly_results['summary']['anomaly_count']} price anomalies across {anomaly_results['summary']['items_with_anomalies']} items."
                insights = anomaly_results["recommendations"]
                anomaly_data = anomaly_results["anomalies"]
            
            # Generate explanation
            explanation = explain_recommendations(intent, text, anomaly_data, insights, insights)
            
            return {
                "intent": "detect_price_anomalies",
                "answer": answer,
                "insights": insights,
                "data": anomaly_data,
                "next_questions": [
                    "Show all purchase orders",
                    "List suppliers",
                    "What's the total spend?",
                    "Show competitive prices"
                ],
                "anomaly_summary": anomaly_results["summary"],
                "recommendations": anomaly_results["recommendations"],
                "explanation": explanation
            }

        if intent == "detect_delayed_orders":
            pos = client.list_purchase_orders(limit=500)
            delay_results = detect_delayed_orders(pos)
            
            if not delay_results["delayed_orders"]:
                answer = "No delayed orders detected. All orders are on schedule!"
                insights = ["Great job maintaining supplier timelines."]
                delay_data = []
            else:
                answer = f"Found {delay_results['summary']['delayed_count']} delayed orders out of {delay_results['summary']['total_orders']} total. On-time delivery: {delay_results['summary']['on_time_percentage']}%."
                insights = delay_results["recommendations"]
                delay_data = delay_results["delayed_orders"]
            
            # Generate explanation
            explanation = explain_recommendations(intent, text, delay_data, insights, insights)
            
            return {
                "intent": "detect_delayed_orders",
                "answer": answer,
                "insights": insights,
                "data": delay_data,
                "next_questions": [
                    "Show purchase orders",
                    "List suppliers",
                    "What's our spending?",
                    "Show price anomalies"
                ],
                "delay_summary": delay_results["summary"],
                "supplier_performance": delay_results["supplier_performance"],
                "recommendations": delay_results["recommendations"],
                "explanation": explanation
            }

        if intent == "analyze_po_risks":
            pos = client.list_purchase_orders(limit=500)
            risk_results = analyze_po_risks(pos, client)
            
            high_count = risk_results["high_risk_count"]
            medium_count = risk_results["medium_risk_count"]
            low_count = risk_results["low_risk_count"]
            
            answer = f"Purchase Order Risk Analysis: {high_count} High Risk | {medium_count} Medium Risk | {low_count} Low Risk"
            
            insights = risk_results["recommendations"]
            
            return {
                "intent": "analyze_po_risks",
                "answer": answer,
                "insights": insights,
                "data": risk_results["orders"],
                "next_questions": [
                    "Show purchase orders",
                    "Show price anomalies",
                    "List suppliers",
                    "What's delayed?"
                ],
                "summary": {
                    "high_risk": high_count,
                    "medium_risk": medium_count,
                    "low_risk": low_count,
                    "total": len(pos)
                },
                "recommendations": risk_results["recommendations"]
            }

        if intent == "list_customers":
            data = client.list_customers()
            answer = f"Found {len(data)} customers."
            insights = [
                f"You have {len(data)} active customers.",
                "Review customer payment status and outstanding amounts.",
                "Monitor customer concentration risk."
            ]
            
            # Generate explanation
            explanation = explain_recommendations(intent, text, data, insights, insights)
            
            return {
                "intent": "list_customers",
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": [
                    "Show sales orders",
                    "List invoices",
                    "What's our revenue?"
                ],
                "explanation": explanation
            }

        if intent == "list_sales_orders":
            data = client.list_sales_orders()
            answer = f"Found {len(data)} sales orders."
            insights = [
                f"You have {len(data)} sales orders.",
                "Review delivery dates to ensure on-time fulfillment.",
                "Monitor sales order status and pending items."
            ]
            return {
                "intent": "list_sales_orders",
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": [
                    "List customers",
                    "Show invoices",
                    "Show purchase orders"
                ]
            }

        if intent == "list_sales_invoices":
            data = client.list_sales_invoices()
            outstanding_total = sum(float(inv.get("outstanding_amount") or 0) for inv in data)
            answer = f"Found {len(data)} invoices. Outstanding amount: ${outstanding_total:,.2f}"
            insights = [
                f"Total invoices: {len(data)}",
                f"Outstanding receivables: ${outstanding_total:,.2f}",
                "Review payment status and follow up on overdue payments."
            ]
            return {
                "intent": "list_sales_invoices",
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": [
                    "List customers",
                    "Show sales orders",
                    "Outstanding payments?"
                ]
            }

        if intent == "list_vendor_bills":
            data = client.list_vendor_bills()
            outstanding_total = sum(float(bill.get("outstanding_amount") or 0) for bill in data)
            answer = f"Found {len(data)} vendor bills. Outstanding amount: ${outstanding_total:,.2f}"
            insights = [
                f"Total vendor bills: {len(data)}",
                f"Outstanding payables: ${outstanding_total:,.2f}",
                "Schedule payments and manage vendor relationships."
            ]
            return {
                "intent": "list_vendor_bills",
                "answer": answer,
                "insights": insights,
                "data": data,
                "next_questions": [
                    "List suppliers",
                    "Show purchase orders",
                    "Delayed orders?"
                ]
            }

        return {
            "intent": "unknown",
            "answer": "I didn't understand that question.",
            "insights": [
                "Try asking about suppliers, items, or purchase orders.",
                "You can also ask about customers, sales orders, or invoices.",
                "Ask about total spend, pending orders, or monthly reports."
            ],
            "data": {},
            "next_questions": [
                "List suppliers",
                "Show customers",
                "Show purchase orders",
                "Show sales orders"
            ]
        }

    except KeyError as e:  # pragma: no cover
        return {
            "intent": intent or "error",
            "answer": f"Missing required data: {str(e)}. Please try a different query.",
            "insights": [],
            "data": {},
            "next_questions": [
                "List suppliers",
                "Show items",
                "Show purchase orders"
            ]
        }
    except ValueError as e:  # pragma: no cover
        return {
            "intent": intent or "error",
            "answer": f"Invalid data format: {str(e)}. Please try again.",
            "insights": [],
            "data": {},
            "next_questions": [
                "List suppliers",
                "Show items",
                "Show purchase orders"
            ]
        }
    except Exception as e:  # pragma: no cover
        return {
            "intent": intent or "error",
            "answer": "An error occurred while processing your request.",
            "insights": [],
            "data": {},
            "next_questions": [
                "List suppliers",
                "Show items",
                "Show purchase orders"
            ]
        }
