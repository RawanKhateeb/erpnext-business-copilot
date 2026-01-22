from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.erpnext_client import ERPNextClient
from pydantic import BaseModel
from app.copilot.service import handle_user_input
import os

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