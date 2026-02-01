"""
Integration tests for real ERPNext running locally.
SKIPS if ERP_URL or ERP_API_KEY not set in environment.
Tests run ONLY locally, NOT in CI.
"""

import unittest
import os
import sys
from fastapi.testclient import TestClient

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class LocalIntegrationTestBase(unittest.TestCase):
    """Base class for local integration tests."""

    @classmethod
    def setUpClass(cls):
        """Skip all tests if ERP_URL or ERP_API_KEY not set."""
        cls.erp_url = os.getenv("ERP_URL")
        cls.erp_api_key = os.getenv("ERP_API_KEY")

        if not cls.erp_url or not cls.erp_api_key:
            raise unittest.SkipTest(
                "ERP_URL or ERP_API_KEY not set. Skipping integration tests."
            )

        cls.client = TestClient(app)

    def setUp(self):
        """Set up before each test."""
        self.client = TestClient(app)


class TestSuppliersIntegration(LocalIntegrationTestBase):
    """Integration tests for suppliers endpoint against real ERPNext."""

    def test_suppliers_endpoint_returns_200(self):
        """Smoke test: suppliers endpoint returns 200."""
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)

    def test_suppliers_endpoint_returns_json_with_data_key(self):
        """Response validation: response contains 'data' key."""
        response = self.client.get("/suppliers")
        data = response.json()
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)


class TestPurchaseOrdersIntegration(LocalIntegrationTestBase):
    """Integration tests for purchase orders endpoint against real ERPNext."""

    def test_purchase_orders_endpoint_returns_200(self):
        """Smoke test: purchase orders endpoint returns 200."""
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)

    def test_purchase_orders_endpoint_returns_json_with_data_key(self):
        """Response validation: response contains 'data' key."""
        response = self.client.get("/purchase-orders")
        data = response.json()
        self.assertIn("data", data)
        self.assertIsInstance(data["data"], list)

    def test_purchase_orders_with_limit_parameter(self):
        """Parameter handling: limit parameter works."""
        response = self.client.get("/purchase-orders?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data["data"]), 5)


class TestPurchaseOrderDetailIntegration(LocalIntegrationTestBase):
    """Integration tests for single purchase order endpoint against real ERPNext."""

    def test_purchase_orders_detail_endpoint_with_valid_po(self):
        """Smoke test: detailed PO endpoint returns 200 for valid PO."""
        # First, fetch a list of POs to get a valid PO name
        list_response = self.client.get("/purchase-orders?limit=1")
        if list_response.status_code == 200:
            pos = list_response.json().get("data", [])
            if pos:
                po_name = pos[0].get("name")
                detail_response = self.client.get(f"/purchase-orders/{po_name}")
                self.assertEqual(detail_response.status_code, 200)
                data = detail_response.json()
                self.assertIn("data", data)


if __name__ == "__main__":
    unittest.main()
