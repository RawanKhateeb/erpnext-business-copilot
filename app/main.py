from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from app.erpnext_client import ERPNextClient
from pydantic import BaseModel
from app.copilot.service import handle_user_input
from app.pdf_export import generate_pdf_report
from app.email_service import send_approval_email, send_report_email
import os
import json

app = FastAPI()

# Lazy-load the client (don't instantiate at module level)
def get_client():
    return ERPNextClient()

# Set up Jinja2 templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/")
def root(request: Request):
    """Serve the Copilot UI homepage."""
    return templates.TemplateResponse("copilot.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/suppliers")
def suppliers():
    try:
        return {"data": get_client().list_suppliers()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/items")
def items():
    try:
        return {"data": get_client().list_items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/purchase-orders")
def purchase_orders(limit: int = 20):
    try:
        return {"data": get_client().list_purchase_orders(limit=limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/purchase-orders/{po_name}")
def purchase_order(po_name: str):
    try:
        return {"data": get_client().get_purchase_order(po_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CopilotRequest(BaseModel):
    query: str

@app.post("/copilot")
def copilot(req: CopilotRequest):
    return handle_user_input(req.query)

@app.post("/copilot/ask")
def copilot_ask(req: CopilotRequest):
    """
    Copilot endpoint: Parse intent and fetch relevant data.
    
    Request: POST /copilot/ask
    Body: { "query": "What suppliers do we have?" }
    
    Response:
    {
        "intent": "list_suppliers",
        "message": "Found 5 suppliers.",
        "data": [...]
    }
    """
    return handle_user_input(req.query)


class ExportRequest(BaseModel):
    data: dict
    intent: str = "report"
    title: str = "ERPNext Copilot Report"


@app.post("/export/pdf")
def export_pdf(req: ExportRequest):
    """
    Export copilot response data as PDF.
    
    Request: POST /export/pdf
    Body: {
        "data": { ... copilot response data ... },
        "intent": "detect_price_anomalies",
        "title": "Price Anomaly Report"
    }
    
    Returns: PDF file download
    """
    try:
        # Extract the data to export
        export_data = req.data.get('data') or req.data
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(
            data=export_data,
            intent=req.intent,
            title=req.title
        )
        
        # Return as downloadable file
        filename = f"copilot_report_{req.intent}.pdf"
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


class EmailRequest(BaseModel):
    recipient_email: str
    data: dict
    intent: str = "report"


@app.post("/send/email")
def send_email(req: EmailRequest):
    """
    Send approval analysis or report via email.
    
    Request: POST /send/email
    Body: {
        "recipient_email": "manager@company.com",
        "data": { ... approval/report data ... },
        "intent": "approve_po"
    }
    
    Returns: {success: bool, message: str}
    """
    try:
        if req.intent == "approve_po":
            # Send approval analysis
            result = send_approval_email(req.recipient_email, req.data)
        else:
            # Send generic report
            result = send_report_email(req.recipient_email, req.data, req.intent)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}"
        }