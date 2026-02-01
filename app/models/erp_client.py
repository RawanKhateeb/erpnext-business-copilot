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

    # -------------------------
    # Customers
    # -------------------------
    def list_customers(self, limit: int = 100):
        url = f"{self.base}/api/resource/Customer"
        params = {
            "limit_page_length": limit,
        }
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    # -------------------------
    # Sales Orders
    # -------------------------
    def list_sales_orders(self, limit: int = 50):
        doctype = quote("Sales Order")
        url = f"{self.base}/api/resource/{doctype}"
        params = {
            "fields": '["name","customer","transaction_date","status","grand_total","delivery_date"]',
            "limit_page_length": limit,
        }
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    def get_sales_order(self, so_name: str):
        doctype = quote("Sales Order")
        url = f"{self.base}/api/resource/{doctype}/{so_name}"
        r = requests.get(url, headers=self.headers, timeout=20)
        r.raise_for_status()
        return r.json().get("data", {})

    # -------------------------
    # Sales Invoices
    # -------------------------
    def list_sales_invoices(self, limit: int = 50):
        doctype = quote("Sales Invoice")
        url = f"{self.base}/api/resource/{doctype}"
        params = {
            "fields": '["name","customer","posting_date","status","grand_total","outstanding_amount"]',
            "limit_page_length": limit,
        }
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])

    # -------------------------
    # Purchase Invoices (Vendor Bills)
    # -------------------------
    def list_vendor_bills(self, limit: int = 50):
        doctype = quote("Purchase Invoice")
        url = f"{self.base}/api/resource/{doctype}"
        params = {
            "fields": '["name","supplier","posting_date","status","grand_total","outstanding_amount"]',
            "limit_page_length": limit,
        }
        r = requests.get(url, headers=self.headers, params=params, timeout=20)
        r.raise_for_status()
        return r.json().get("data", [])
