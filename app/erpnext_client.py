import requests
from urllib.parse import quote
from app.config import ERP_URL, ERP_API_KEY, ERP_API_SECRET


class ERPNextClient:
    def __init__(self):
        if not ERP_URL or not ERP_API_KEY or not ERP_API_SECRET:
            raise RuntimeError(
                "Missing ERP env vars (ERP_URL / ERP_API_KEY / ERP_API_SECRET). Check .env loading"
            )

        self.base = ERP_URL.rstrip("/")
        self.headers = {
            "Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}"
        }

    # -------------------------
    # Suppliers
    # -------------------------
    def list_suppliers(self):
        url = f"{self.base}/api/resource/Supplier"
        r = requests.get(url, headers=self.headers, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    # -------------------------
    # Items
    # -------------------------
    def list_items(self):
        url = f"{self.base}/api/resource/Item"
        params = {
            "fields": '["name","item_name"]'
        }
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    # -------------------------
    # Purchase Orders
    # -------------------------
    def list_purchase_orders(self, limit: int = 20):
        doctype = quote("Purchase Order")  # Purchase%20Order
        url = f"{self.base}/api/resource/{doctype}"

        params = {
            "fields": '["name","supplier","transaction_date","status","grand_total"]',
            "limit_page_length": limit,
        }

        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    def get_purchase_order(self, po_name: str):
        doctype = quote("Purchase Order")
        url = f"{self.base}/api/resource/{doctype}/{po_name}"

        r = requests.get(url, headers=self.headers, timeout=20)
        r.raise_for_status()
        return r.json().get("data", {})
