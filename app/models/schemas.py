"""Data schemas (Pydantic models)."""
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request model for copilot queries."""
    query: str


class PurchaseOrderExportRequest(BaseModel):
    """Request model for PO export."""
    po_name: str


class AIReportRequest(BaseModel):
    """Request model for AI report generation."""
    query: str
