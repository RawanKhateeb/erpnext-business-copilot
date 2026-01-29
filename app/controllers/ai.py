"""AI controllers - Report generation."""
from fastapi import APIRouter, HTTPException
import logging
from app.models import AIReportRequest, ERPNextClient
from app.services.ai_report_generator import AIReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai"])


def get_client():
    """Lazy-load ERPNext client."""
    return ERPNextClient()


def _compute_po_summary(pos):
    """Compute summary statistics from purchase orders."""
    if not pos:
        return {
            "po_count": 0,
            "total_spend": 0,
            "average_order_value": 0,
            "top_suppliers": [],
            "status_breakdown": {},
        }

    # Calculate total spend
    total_spend = sum(float(po.get("grand_total", 0)) for po in pos if po.get("grand_total"))
    
    # Calculate spend by supplier (not just count)
    suppliers_spend = {}
    for po in pos:
        supplier = po.get("supplier", "Unknown")
        amount = float(po.get("grand_total", 0))
        suppliers_spend[supplier] = suppliers_spend.get(supplier, 0) + amount
    
    # Top suppliers by spend
    top_suppliers = sorted(suppliers_spend.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Status breakdown
    status_breakdown = {}
    for po in pos:
        status = po.get("status", "Unknown")
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    pending_count = status_breakdown.get("Pending", 0)

    return {
        "po_count": len(pos),
        "total_spend": round(total_spend, 2),
        "average_order_value": round(total_spend / len(pos), 2) if pos else 0,
        "top_suppliers": top_suppliers,  # List of (supplier_name, total_spend) tuples
        "status_breakdown": status_breakdown,
        "pending_count": pending_count,
    }


@router.post("/ai/report")
def ai_report(req: AIReportRequest):
    """
    Generate AI-powered procurement report using OpenAI.
    
    Request: POST /ai/report
    Body: {"query": "Generate monthly procurement report"}
    
    Returns: {
        "success": true,
        "intent": "ai_report",
        "answer": "Narrative report text",
        "ai_generated": true,
        "summary": {...}
    }
    """
    try:
        logger.info(f"AI Report request: {req.query}")
        
        # Step 1: Fetch purchase orders from ERPNext
        try:
            client = get_client()
            pos = client.list_purchase_orders()
            logger.info(f"Fetched {len(pos) if pos else 0} purchase orders")
        except Exception as e:
            logger.error(f"ERPNext fetch error: {str(e)}")
            pos = []
        
        if not pos:
            logger.warning("No purchase orders found")
            return {
                "success": False,
                "message": "No purchase order data available",
                "intent": "ai_report",
                "ai_generated": True
            }
        
        # Step 2: Compute summary statistics
        try:
            summary = _compute_po_summary(pos)
            summary['date_range'] = 'This Period'
            logger.info(f"Summary computed: {summary['po_count']} orders, ${summary['total_spend']} total spend")
        except Exception as e:
            logger.error(f"Summary computation error: {str(e)}")
            return {
                "success": False,
                "message": f"Error computing summary: {str(e)}",
                "intent": "ai_report",
                "ai_generated": True
            }
        
        # Step 3: Generate AI report
        try:
            logger.info("Creating AIReportGenerator...")
            ai_gen = AIReportGenerator()
            logger.info("AIReportGenerator created, calling generate_procurement_report...")
            
            result = ai_gen.generate_procurement_report(summary, req.query)
            logger.info(f"AI generation result: success={result.get('success')}")
            
            if result.get('success'):
                logger.info("Report generated successfully")
                return {
                    "success": True,
                    "intent": "ai_report",
                    "answer": result['report'],
                    "ai_generated": True,
                    "summary": result['summary'],
                    "generated_at": result['generated_at']
                }
            else:
                error_msg = result.get('message', 'AI service unavailable')
                logger.error(f"AI Report generation failed: {error_msg}")
                return {
                    "success": False,
                    "message": error_msg,
                    "intent": "ai_report",
                    "ai_generated": True,
                    "error": result.get('error')
                }
        except Exception as e:
            logger.error(f"AI generation error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error generating report: {str(e)}",
                "intent": "ai_report",
                "ai_generated": True,
                "error": str(e)
            }
    except Exception as e:
        logger.error(f"Unexpected error in ai_report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
