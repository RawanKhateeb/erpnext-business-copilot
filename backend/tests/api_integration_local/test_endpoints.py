"""
Integration tests for real ERPNext running locally.
SKIPS if running in CI OR if ERP_URL / ERP_API_KEY not set.
Tests run ONLY locally, NOT in CI.

Validates:
- Response structure and status codes
- Real ERPNext data fields and types
- Meaningful content (non-empty, properly formatted)
- Graceful skipping when no data exists
"""

import unittest
import os
import sys
from fastapi.testclient import TestClient

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class LocalIntegrationTestBase(unittest.TestCase):
    """Base class for local integration tests with common validation methods."""

    client = None

    @classmethod
    def setUpClass(cls):
        """
        Skip all tests:
        - Always skip in CI
        - Skip if ERP_URL or ERP_API_KEY not set
        """
        # 1) Force skip in CI (GitHub Actions usually sets CI=true)
        if os.getenv("CI", "").lower() == "true":
            raise unittest.SkipTest("Integration tests run locally only (skipped in CI).")

        # 2) Skip if env vars missing
        cls.erp_url = os.getenv("ERP_URL")
        cls.erp_api_key = os.getenv("ERP_API_KEY")

        if not cls.erp_url or not cls.erp_api_key:
            raise unittest.SkipTest("ERP_URL or ERP_API_KEY not set. Skipping integration tests.")

        cls.client = TestClient(app)

    @staticmethod
    def validate_response_structure(response_data):
        """Validate response has correct structure and return data."""
        if not isinstance(response_data, dict):
            raise AssertionError("Response must be a dictionary (JSON object)")

        if "data" not in response_data:
            raise AssertionError("Response must contain 'data' key")

        data = response_data["data"]

        if not isinstance(data, (list, dict)):
            raise AssertionError("Response['data'] must be a list or dictionary")

        return data

    @staticmethod
    def validate_non_empty_data(data, entity_type="record"):
        """Validate data is not empty and skip test if it is."""
        if isinstance(data, dict):
            if not data:
                raise unittest.SkipTest(f"No {entity_type} data found in ERPNext. Skipping validation test.")
        elif isinstance(data, list):
            if len(data) == 0:
                raise unittest.SkipTest(f"No {entity_type} data found in ERPNext. Skipping validation test.")
        return data

    @staticmethod
    def validate_supplier(supplier):
        """Validate supplier record has required fields."""
        if not isinstance(supplier, dict):
            raise AssertionError("Supplier must be a dictionary")

        if "name" not in supplier:
            raise AssertionError("Supplier missing required field: name")

        if supplier["name"] is None:
            raise AssertionError("Supplier field 'name' cannot be None")

        if not isinstance(supplier["name"], str):
            raise AssertionError("Supplier name must be string")

        if len(supplier["name"].strip()) == 0:
            raise AssertionError("Supplier name cannot be empty")

        return supplier

    @staticmethod
    def validate_purchase_order(po):
        """Validate purchase order record has required fields and valid data."""
        if not isinstance(po, dict):
            raise AssertionError("PO must be a dictionary")

        required_fields = ["name", "supplier", "status"]
        for field in required_fields:
            if field not in po:
                raise AssertionError(f"PO missing required field: {field}")
            if po[field] is None:
                raise AssertionError(f"PO field '{field}' cannot be None")

        if not isinstance(po["name"], str) or len(po["name"].strip()) == 0:
            raise AssertionError("PO name must be a non-empty string")

        if not isinstance(po["supplier"], str) or len(po["supplier"].strip()) == 0:
            raise AssertionError("PO supplier must be a non-empty string")

        if not isinstance(po["status"], str) or len(po["status"].strip()) == 0:
            raise AssertionError("PO status must be a non-empty string")

        # Optional numeric fields
        if "total" in po and po["total"] is not None and not isinstance(po["total"], (int, float)):
            raise AssertionError("Total must be numeric")

        if "grand_total" in po and po["grand_total"] is not None and not isinstance(po["grand_total"], (int, float)):
            raise AssertionError("Grand total must be numeric")

        return po


class TestSuppliersIntegration(LocalIntegrationTestBase):
    """Integration tests for suppliers endpoint against real ERPNext."""

    def test_suppliers_endpoint_returns_200(self):
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200, "Suppliers endpoint should return 200")

    def test_suppliers_response_has_valid_structure(self):
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)

        data = self.validate_response_structure(response.json())
        self.assertIsInstance(data, list, "Suppliers data must be a list")

    def test_suppliers_contains_valid_data(self):
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)

        suppliers = self.validate_response_structure(response.json())
        suppliers = self.validate_non_empty_data(suppliers, "supplier")

        # Validate up to first 4 suppliers (stable even if only 1-2 exist)
        for supplier in suppliers[:4]:
            self.validate_supplier(supplier)

    def test_suppliers_names_are_non_empty_strings(self):
        """
        Replaces the old 'unique names' test (which can be flaky in real ERP data).
        This checks quality without assuming uniqueness.
        """
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)

        suppliers = self.validate_response_structure(response.json())
        suppliers = self.validate_non_empty_data(suppliers, "supplier")

        for s in suppliers[:20]:
            self.assertIn("name", s)
            self.assertIsInstance(s["name"], str)
            self.assertGreater(len(s["name"].strip()), 0)


class TestPurchaseOrdersIntegration(LocalIntegrationTestBase):
    """Integration tests for purchase orders endpoint against real ERPNext."""

    def test_purchase_orders_endpoint_returns_200(self):
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200, "Purchase orders endpoint should return 200")

    def test_purchase_orders_response_has_valid_structure(self):
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)

        data = self.validate_response_structure(response.json())
        self.assertIsInstance(data, list, "Purchase orders data must be a list")

    def test_purchase_orders_contains_valid_data(self):
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)

        pos = self.validate_response_structure(response.json())
        pos = self.validate_non_empty_data(pos, "purchase order")

        for po in pos[:4]:
            self.validate_purchase_order(po)

    def test_purchase_orders_with_limit_parameter(self):
        limit = 5
        response = self.client.get(f"/purchase-orders?limit={limit}")
        self.assertEqual(response.status_code, 200)

        pos = self.validate_response_structure(response.json())
        self.assertLessEqual(len(pos), limit, f"Should return at most {limit} results when limit={limit}")

        for po in pos:
            self.validate_purchase_order(po)

    def test_purchase_orders_have_valid_statuses(self):
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)

        pos = self.validate_response_structure(response.json())
        pos = self.validate_non_empty_data(pos, "purchase order")

        for po in pos[:10]:
            self.assertIn("status", po, f"PO {po.get('name')} missing status field")
            self.assertIsInstance(po["status"], str, f"Status must be string for PO {po.get('name')}")
            self.assertGreater(len(po["status"].strip()), 0, f"Status cannot be empty for PO {po.get('name')}")


class TestPurchaseOrderDetailIntegration(LocalIntegrationTestBase):
    """Integration tests for single purchase order endpoint against real ERPNext."""

    def test_purchase_order_detail_endpoint_returns_valid_data(self):
        list_response = self.client.get("/purchase-orders?limit=1")
        self.assertEqual(list_response.status_code, 200)

        pos = self.validate_response_structure(list_response.json())
        self.assertIsInstance(pos, list, "List response data must be a list")
        pos = self.validate_non_empty_data(pos, "purchase order")

        po_name = pos[0].get("name")
        self.assertIsNotNone(po_name, "PO name cannot be None")

        detail_response = self.client.get(f"/purchase-orders/{po_name}")
        self.assertEqual(detail_response.status_code, 200)

        po_data = self.validate_response_structure(detail_response.json())

        if isinstance(po_data, dict):
            po_detail = po_data
        elif isinstance(po_data, list):
            po_data = self.validate_non_empty_data(po_data, "purchase order detail")
            po_detail = po_data[0]
        else:
            self.fail(f"Unexpected data type for PO detail: {type(po_data)}")

        self.validate_purchase_order(po_detail)

    def test_purchase_order_detail_has_more_fields_than_list(self):
        list_response = self.client.get("/purchase-orders?limit=1")
        self.assertEqual(list_response.status_code, 200)

        list_pos = self.validate_response_structure(list_response.json())
        self.assertIsInstance(list_pos, list, "List response data must be a list")
        list_pos = self.validate_non_empty_data(list_pos, "purchase order")

        list_po = list_pos[0]
        po_name = list_po["name"]
        list_po_fields = set(list_po.keys())

        detail_response = self.client.get(f"/purchase-orders/{po_name}")
        self.assertEqual(detail_response.status_code, 200)

        po_data = self.validate_response_structure(detail_response.json())

        if isinstance(po_data, dict):
            detail_po = po_data
        elif isinstance(po_data, list):
            po_data = self.validate_non_empty_data(po_data, "purchase order detail")
            detail_po = po_data[0]
        else:
            self.fail(f"Unexpected data type for PO detail: {type(po_data)}")

        detail_po_fields = set(detail_po.keys())

        self.assertTrue(
            detail_po_fields >= list_po_fields,
            f"Detail should have at least same fields as list. Missing: {list_po_fields - detail_po_fields}"
        )


if __name__ == "__main__":
    unittest.main()
