"""Data controllers - Suppliers, Items, Purchase Orders, etc."""
from fastapi import APIRouter, HTTPException
from app.models import ERPNextClient

router = APIRouter(tags=["data"])


def get_client():  # pragma: no cover
    """Lazy-load ERPNext client."""
    return ERPNextClient()


@router.get("/suppliers")
def list_suppliers():
    """List all suppliers."""
    try:
        return {"data": get_client().list_suppliers()}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items")
def list_items():
    """List all items."""
    try:
        return {"data": get_client().list_items()}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchase-orders")
def list_purchase_orders(limit: int = 20):
    """List purchase orders."""
    try:
        return {"data": get_client().list_purchase_orders(limit)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/purchase-orders/{po_name}")
def get_purchase_order(po_name: str):
    """Get details of a specific purchase order."""
    try:
        return {"data": get_client().get_purchase_order(po_name)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers")
def list_customers(limit: int = 100):
    """List all customers."""
    try:
        return {"data": get_client().list_customers(limit)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-orders")
def list_sales_orders(limit: int = 50):
    """List sales orders."""
    try:
        return {"data": get_client().list_sales_orders(limit)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-orders/{so_name}")
def get_sales_order(so_name: str):
    """Get details of a specific sales order."""
    try:
        return {"data": get_client().get_sales_order(so_name)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-invoices")
def list_sales_invoices(limit: int = 50):
    """List sales invoices."""
    try:
        return {"data": get_client().list_sales_invoices(limit)}
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-invoices/{si_name}")
def get_sales_invoice(si_name: str):
    """Get details of a specific sales invoice."""
    try:
        return {"data": get_client().get_sales_invoice(si_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotations")
def list_quotations(limit: int = 50):
    """List quotations."""
    try:
        return {"data": get_client().list_quotations(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotations/{qtn_name}")
def get_quotation(qtn_name: str):
    """Get details of a specific quotation."""
    try:
        return {"data": get_client().get_quotation(qtn_name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
