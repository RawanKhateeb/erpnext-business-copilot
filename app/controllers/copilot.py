"""Copilot controllers - Query handling."""
from fastapi import APIRouter
from app.models import QueryRequest
from app.copilot.service import handle_user_input

router = APIRouter(tags=["copilot"])


@router.post("/copilot")
def copilot(req: QueryRequest):
    """Handle copilot query."""
    return handle_user_input(req.query)


@router.post("/copilot/ask")
def copilot_ask(req: QueryRequest):
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
