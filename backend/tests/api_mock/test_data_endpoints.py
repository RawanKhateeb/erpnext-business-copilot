"""
Unittest-based API tests for data endpoints.
Tests all 11 data endpoints using FastAPI TestClient and unittest.mock.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app
from backend.tests.api_mock.mock_data import (
    MOCK_SUPPLIERS,
    MOCK_ITEMS,
    MOCK_PURCHASE_ORDERS,
    MOCK_PURCHASE_ORDER_DETAIL,
    MOCK_SALES_ORDERS,
    MOCK_SALES_INVOICES,
    MOCK_CUSTOMERS,
    MOCK_QUOTATIONS,
)


class TestDataEndpoints(unittest.TestCase):
    """Test all data endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    def setUp(self):
        """Set up before each test - create fresh mocks."""
        self.mock_client_patcher = patch('app.controllers.data.get_client')
        self.mock_get_client = self.mock_client_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.mock_client_patcher.stop()

    # ============ GET /suppliers ============
    @patch('app.controllers.data.get_client')
    def test_get_suppliers_success(self, mock_get_client):
        """Test GET /suppliers returns supplier list."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS
        mock_get_client.return_value = mock_client

        response = self.client.get("/suppliers")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["data"][0]["name"], "Supplier A")

    @patch('app.controllers.data.get_client')
    def test_get_suppliers_empty_list(self, mock_get_client):
        """Test GET /suppliers with empty list."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = []
        mock_get_client.return_value = mock_client

        response = self.client.get("/suppliers")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"]), 0)

    @patch('app.controllers.data.get_client')
    def test_get_suppliers_error(self, mock_get_client):
        """Test GET /suppliers error handling."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("Connection failed")
        mock_get_client.return_value = mock_client

        response = self.client.get("/suppliers")

        self.assertEqual(response.status_code, 500)

    # ============ GET /items ============
    @patch('app.controllers.data.get_client')
    def test_get_items_success(self, mock_get_client):
        """Test GET /items returns item list."""
        mock_client = MagicMock()
        mock_client.list_items.return_value = MOCK_ITEMS
        mock_get_client.return_value = mock_client

        response = self.client.get("/items")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["data"][0]["item_code"], "Item-001")

    @patch('app.controllers.data.get_client')
    def test_get_items_error(self, mock_get_client):
        """Test GET /items error handling."""
        mock_client = MagicMock()
        mock_client.list_items.side_effect = Exception("DB error")
        mock_get_client.return_value = mock_client

        response = self.client.get("/items")

        self.assertEqual(response.status_code, 500)

    # ============ GET /purchase-orders ============
    @patch('app.controllers.data.get_client')
    def test_get_purchase_orders_success(self, mock_get_client):
        """Test GET /purchase-orders returns PO list."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS
        mock_get_client.return_value = mock_client

        response = self.client.get("/purchase-orders")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["data"][0]["name"], "PO-2024-001")

    @patch('app.controllers.data.get_client')
    def test_get_purchase_orders_with_limit(self, mock_get_client):
        """Test GET /purchase-orders with limit parameter."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS[:1]
        mock_get_client.return_value = mock_client

        response = self.client.get("/purchase-orders?limit=1")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        mock_client.list_purchase_orders.assert_called_with(1)

    @patch('app.controllers.data.get_client')
    def test_get_purchase_orders_error(self, mock_get_client):
        """Test GET /purchase-orders error handling."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.side_effect = Exception("ERP unavailable")
        mock_get_client.return_value = mock_client

        response = self.client.get("/purchase-orders")

        self.assertEqual(response.status_code, 500)

    # ============ GET /purchase-orders/{po_name} ============
    @patch('app.controllers.data.get_client')
    def test_get_purchase_order_by_name(self, mock_get_client):
        """Test GET /purchase-orders/{po_name} returns PO details."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = MOCK_PURCHASE_ORDER_DETAIL
        mock_get_client.return_value = mock_client

        response = self.client.get("/purchase-orders/PO-2024-001")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(data["data"]["name"], "PO-2024-001")
        self.assertEqual(data["data"]["supplier"], "Supplier A")
        mock_client.get_purchase_order.assert_called_with("PO-2024-001")

    @patch('app.controllers.data.get_client')
    def test_get_purchase_order_not_found(self, mock_get_client):
        """Test GET /purchase-orders/{po_name} when PO not found."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.side_effect = Exception("Not found")
        mock_get_client.return_value = mock_client

        response = self.client.get("/purchase-orders/INVALID-PO")

        self.assertEqual(response.status_code, 500)

    # ============ GET /customers ============
    @patch('app.controllers.data.get_client')
    def test_get_customers_success(self, mock_get_client):
        """Test GET /customers returns customer list."""
        mock_client = MagicMock()
        mock_client.list_customers.return_value = MOCK_CUSTOMERS
        mock_get_client.return_value = mock_client

        response = self.client.get("/customers")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 2)

    @patch('app.controllers.data.get_client')
    def test_get_customers_with_limit(self, mock_get_client):
        """Test GET /customers with limit parameter."""
        mock_client = MagicMock()
        mock_client.list_customers.return_value = MOCK_CUSTOMERS[:1]
        mock_get_client.return_value = mock_client

        response = self.client.get("/customers?limit=1")

        self.assertEqual(response.status_code, 200)
        mock_client.list_customers.assert_called_with(1)

    # ============ GET /sales-orders ============
    @patch('app.controllers.data.get_client')
    def test_get_sales_orders_success(self, mock_get_client):
        """Test GET /sales-orders returns sales order list."""
        mock_client = MagicMock()
        mock_client.list_sales_orders.return_value = MOCK_SALES_ORDERS
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-orders")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)

    @patch('app.controllers.data.get_client')
    def test_get_sales_orders_with_limit(self, mock_get_client):
        """Test GET /sales-orders with limit parameter."""
        mock_client = MagicMock()
        mock_client.list_sales_orders.return_value = MOCK_SALES_ORDERS
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-orders?limit=25")

        self.assertEqual(response.status_code, 200)
        mock_client.list_sales_orders.assert_called_with(25)

    # ============ GET /sales-orders/{so_name} ============
    @patch('app.controllers.data.get_client')
    def test_get_sales_order_by_name(self, mock_get_client):
        """Test GET /sales-orders/{so_name} returns SO details."""
        mock_client = MagicMock()
        mock_so = {"name": "SO-2024-001", "customer": "Customer A", "grand_total": 5000}
        mock_client.get_sales_order.return_value = mock_so
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-orders/SO-2024-001")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["data"]["name"], "SO-2024-001")
        mock_client.get_sales_order.assert_called_with("SO-2024-001")

    # ============ GET /sales-invoices ============
    @patch('app.controllers.data.get_client')
    def test_get_sales_invoices_success(self, mock_get_client):
        """Test GET /sales-invoices returns invoice list."""
        mock_client = MagicMock()
        mock_client.list_sales_invoices.return_value = MOCK_SALES_INVOICES
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-invoices")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)

    @patch('app.controllers.data.get_client')
    def test_get_sales_invoices_with_limit(self, mock_get_client):
        """Test GET /sales-invoices with limit parameter."""
        mock_client = MagicMock()
        mock_client.list_sales_invoices.return_value = MOCK_SALES_INVOICES
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-invoices?limit=10")

        self.assertEqual(response.status_code, 200)
        mock_client.list_sales_invoices.assert_called_with(10)

    # ============ GET /sales-invoices/{si_name} ============
    @patch('app.controllers.data.get_client')
    def test_get_sales_invoice_by_name(self, mock_get_client):
        """Test GET /sales-invoices/{si_name} returns invoice details."""
        mock_client = MagicMock()
        mock_si = {"name": "SI-2024-001", "customer": "Customer A", "grand_total": 3000}
        mock_client.get_sales_invoice.return_value = mock_si
        mock_get_client.return_value = mock_client

        response = self.client.get("/sales-invoices/SI-2024-001")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["data"]["name"], "SI-2024-001")
        mock_client.get_sales_invoice.assert_called_with("SI-2024-001")

    # ============ GET /quotations ============
    @patch('app.controllers.data.get_client')
    def test_get_quotations_success(self, mock_get_client):
        """Test GET /quotations returns quotation list."""
        mock_client = MagicMock()
        mock_client.list_quotations.return_value = MOCK_QUOTATIONS
        mock_get_client.return_value = mock_client

        response = self.client.get("/quotations")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertGreater(len(data["data"]), 0)

    @patch('app.controllers.data.get_client')
    def test_get_quotations_with_limit(self, mock_get_client):
        """Test GET /quotations with limit parameter."""
        mock_client = MagicMock()
        mock_client.list_quotations.return_value = MOCK_QUOTATIONS
        mock_get_client.return_value = mock_client

        response = self.client.get("/quotations?limit=15")

        self.assertEqual(response.status_code, 200)
        mock_client.list_quotations.assert_called_with(15)

    # ============ GET /quotations/{qtn_name} ============
    @patch('app.controllers.data.get_client')
    def test_get_quotation_by_name(self, mock_get_client):
        """Test GET /quotations/{qtn_name} returns quotation details."""
        mock_client = MagicMock()
        mock_qtn = {"name": "QTN-2024-001", "customer": "Customer B", "grand_total": 2500}
        mock_client.get_quotation.return_value = mock_qtn
        mock_get_client.return_value = mock_client

        response = self.client.get("/quotations/QTN-2024-001")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["data"]["name"], "QTN-2024-001")
        mock_client.get_quotation.assert_called_with("QTN-2024-001")


if __name__ == "__main__":
    unittest.main()
