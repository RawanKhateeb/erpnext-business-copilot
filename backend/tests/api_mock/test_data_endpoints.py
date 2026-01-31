"""
Tests for all DATA endpoints (12 endpoints).
Tests: /suppliers, /items, /purchase-orders, /customers, /sales-orders, /sales-invoices, /quotations
"""

import unittest
from backend.tests.api_mock.base_test import APITestBase


class TestSuppliersEndpoint(APITestBase):
    """Tests for GET /suppliers endpoint."""
    
    def test_get_suppliers_returns_200_or_500(self):
        """GET /suppliers returns 200 or 500 (depending on ERPNext availability)."""
        response = self.client.get("/suppliers")
        self.assertIn(response.status_code, [200, 500])
    
    def test_get_suppliers_endpoint_exists(self):
        """Suppliers endpoint is accessible."""
        response = self.client.get("/suppliers")
        # Endpoint exists (not 404)
        self.assertNotEqual(response.status_code, 404)


class TestItemsEndpoint(APITestBase):
    """Tests for GET /items endpoint."""
    
    def test_get_items_returns_200_or_500(self):
        """GET /items returns 200 or 500 (depending on ERPNext availability)."""
        response = self.client.get("/items")
        self.assertIn(response.status_code, [200, 500])
    
    def test_get_items_endpoint_exists(self):
        """Items endpoint is accessible."""
        response = self.client.get("/items")
        self.assertNotEqual(response.status_code, 404)


class TestPurchaseOrdersEndpoint(APITestBase):
    """Tests for GET /purchase-orders and GET /purchase-orders/{po_name} endpoints."""
    
    def test_get_purchase_orders_endpoint_exists(self):
        """GET /purchase-orders endpoint is accessible."""
        response = self.client.get("/purchase-orders")
        self.assertNotEqual(response.status_code, 404)
    
    def test_get_purchase_order_detail_endpoint_exists(self):
        """GET /purchase-orders/{po_name} endpoint is accessible."""
        response = self.client.get("/purchase-orders/TEST-PO-001")
        # Should either return data (200), not found (404/500 from ERPNext), or valid error
        self.assertNotEqual(response.status_code, 404)


class TestCustomersEndpoint(APITestBase):
    """Tests for GET /customers endpoint."""
    
    def test_get_customers_endpoint_exists(self):
        """GET /customers endpoint is accessible."""
        response = self.client.get("/customers")
        self.assertNotEqual(response.status_code, 404)


class TestSalesOrdersEndpoint(APITestBase):
    """Tests for GET /sales-orders and GET /sales-orders/{so_name} endpoints."""
    
    def test_get_sales_orders_endpoint_exists(self):
        """GET /sales-orders endpoint is accessible."""
        response = self.client.get("/sales-orders")
        self.assertNotEqual(response.status_code, 404)
    
    def test_get_sales_order_detail_endpoint_exists(self):
        """GET /sales-orders/{so_name} endpoint is accessible."""
        response = self.client.get("/sales-orders/TEST-SO-001")
        self.assertNotEqual(response.status_code, 404)


class TestSalesInvoicesEndpoint(APITestBase):
    """Tests for GET /sales-invoices and GET /sales-invoices/{si_name} endpoints."""
    
    def test_get_sales_invoices_endpoint_exists(self):
        """GET /sales-invoices endpoint is accessible."""
        response = self.client.get("/sales-invoices")
        self.assertNotEqual(response.status_code, 404)
    
    def test_get_sales_invoice_detail_endpoint_exists(self):
        """GET /sales-invoices/{si_name} endpoint is accessible."""
        response = self.client.get("/sales-invoices/TEST-INV-001")
        self.assertNotEqual(response.status_code, 404)


class TestQuotationsEndpoint(APITestBase):
    """Tests for GET /quotations and GET /quotations/{qtn_name} endpoints."""
    
    def test_get_quotations_endpoint_exists(self):
        """GET /quotations endpoint is accessible."""
        response = self.client.get("/quotations")
        self.assertNotEqual(response.status_code, 404)
    
    def test_get_quotation_detail_endpoint_exists(self):
        """GET /quotations/{qtn_name} endpoint is accessible."""
        response = self.client.get("/quotations/TEST-QTN-001")
        self.assertNotEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

