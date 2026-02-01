"""Export controllers - PDF generation."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.pdf_export import generate_pdf_report

router = APIRouter(tags=["export"])


class ExportRequest(BaseModel):
    """Request model for PDF export."""
    data: dict
    intent: str = "report"
    title: str = "ERPNext Copilot Report"


@router.post("/export/pdf")
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
