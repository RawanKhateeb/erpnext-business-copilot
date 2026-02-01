"""
Integration tests for real ERPNext running locally.
SKIPS if ERP_URL or ERP_API_KEY not set in environment.
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
        """Skip all tests if ERP_URL or ERP_API_KEY not set."""
        cls.erp_url = os.getenv("ERP_URL")
        cls.erp_api_key = os.getenv("ERP_API_KEY")

        if not cls.erp_url or not cls.erp_api_key:
            raise unittest.SkipTest(
                "ERP_URL or ERP_API_KEY not set. Skipping integration tests."
            )

        cls.client = TestClient(app)

    @staticmethod
    def validate_response_structure(response_data):
        """Validate response has correct structure and return data."""
        if not isinstance(response_data, dict):
            raise AssertionError("Response must be a dictionary")
        if "data" not in response_data:
            raise AssertionError("Response must contain 'data' key")
        
        data = response_data["data"]
        # Handle both list and dict responses
        if not isinstance(data, (list, dict)):
            raise AssertionError("Data must be a list or dictionary")
        
        return data

    @staticmethod
    def validate_non_empty_data(data, entity_type="record"):
        """Validate data is not empty and skip test if it is."""
        if isinstance(data, dict):
            # If dict, check if it has content
            if not data:
                raise unittest.SkipTest(f"No {entity_type} data found in ERPNext. Skipping validation test.")
        elif isinstance(data, list):
            # If list, check length
            if len(data) == 0:
                raise unittest.SkipTest(f"No {entity_type} data found in ERPNext. Skipping validation test.")
        return data

    @staticmethod
    def validate_supplier(supplier):
        """Validate supplier record has required fields."""
        if not isinstance(supplier, dict):
            raise AssertionError("Supplier must be a dictionary")
        
        # Check required fields exist
        if "name" not in supplier:
            raise AssertionError("Supplier missing required field: name")
        if supplier["name"] is None:
            raise AssertionError("Supplier field 'name' cannot be None")
        
        # Validate field types
        if not isinstance(supplier["name"], str):
            raise AssertionError("Supplier name must be string")
        if len(supplier["name"]) == 0:
            raise AssertionError("Supplier name cannot be empty")
        
        return supplier

    @staticmethod
    def validate_purchase_order(po):
        """Validate purchase order record has required fields and valid data."""
        if not isinstance(po, dict):
            raise AssertionError("PO must be a dictionary")
        
        # Check required fields exist
        required_fields = ["name", "supplier", "status"]
        for field in required_fields:
            if field not in po:
                raise AssertionError(f"PO missing required field: {field}")
            if po[field] is None:
                raise AssertionError(f"PO field '{field}' cannot be None")
        
        # Validate field types
        if not isinstance(po["name"], str):
            raise AssertionError("PO name must be string")
        if len(po["name"]) == 0:
            raise AssertionError("PO name cannot be empty")
        if not isinstance(po["supplier"], str):
            raise AssertionError("Supplier must be string")
        if not isinstance(po["status"], str):
            raise AssertionError("Status must be string")
        if len(po["status"]) == 0:
            raise AssertionError("Status cannot be empty")
        
        # Validate numeric fields if present
        if "total" in po and po["total"] is not None:
            if not isinstance(po["total"], (int, float)):
                raise AssertionError("Total must be numeric")
        
        if "grand_total" in po and po["grand_total"] is not None:
            if not isinstance(po["grand_total"], (int, float)):
                raise AssertionError("Grand total must be numeric")
        
        return po


class TestSuppliersIntegration(LocalIntegrationTestBase):
    """Integration tests for suppliers endpoint against real ERPNext."""

    def test_suppliers_endpoint_returns_200(self):
        """Smoke test: suppliers endpoint returns 200."""
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200, "Suppliers endpoint should return 200")

    def test_suppliers_response_has_valid_structure(self):
        """Validate response structure."""
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)
        data = self.validate_response_structure(response.json())
        self.assertIsInstance(data, list, "Suppliers data must be a list")

    def test_suppliers_contains_valid_data(self):
        """Validate suppliers contain actual supplier records with required fields."""
        response = self.client.get("/suppliers")
        self.assertEqual(response.status_code, 200)
        
        suppliers = self.validate_response_structure(response.json())
        suppliers = self.validate_non_empty_data(suppliers, "supplier")
        
        # Validate first supplier has required fields
        first_supplier = suppliers[0]
        self.validate_supplier(first_supplier)
        
        # Spot-check next 3 suppliers for consistency
        for supplier in suppliers[1:4]:
            self.validate_supplier(supplier)

    def test_suppliers_have_unique_names(self):
        """Validate all suppliers have unique names."""
        response = self.client.get("/suppliers")
        suppliers = self.validate_response_structure(response.json())
        suppliers = self.validate_non_empty_data(suppliers, "supplier")
        
        supplier_names = [s["name"] for s in suppliers]
        unique_names = set(supplier_names)
        
        self.assertEqual(
            len(supplier_names), 
            len(unique_names),
            "Supplier names should be unique"
        )


class TestPurchaseOrdersIntegration(LocalIntegrationTestBase):
    """Integration tests for purchase orders endpoint against real ERPNext."""

    def test_purchase_orders_endpoint_returns_200(self):
        """Smoke test: purchase orders endpoint returns 200."""
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200, "Purchase orders endpoint should return 200")

    def test_purchase_orders_response_has_valid_structure(self):
        """Validate response structure."""
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)
        data = self.validate_response_structure(response.json())
        self.assertIsInstance(data, list, "Purchase orders data must be a list")

    def test_purchase_orders_contains_valid_data(self):
        """Validate purchase orders contain actual PO records with required fields."""
        response = self.client.get("/purchase-orders")
        self.assertEqual(response.status_code, 200)
        
        pos = self.validate_response_structure(response.json())
        pos = self.validate_non_empty_data(pos, "purchase order")
        
        # Validate first PO has required fields
        first_po = pos[0]
        self.validate_purchase_order(first_po)
        
        # Spot-check next 3 POs for consistency
        for po in pos[1:4]:
            self.validate_purchase_order(po)

    def test_purchase_orders_with_limit_parameter(self):
        """Parameter handling: limit parameter correctly restricts results."""
        limit = 5
        response = self.client.get(f"/purchase-orders?limit={limit}")
        self.assertEqual(response.status_code, 200)
        
        pos = self.validate_response_structure(response.json())
        self.assertLessEqual(
            len(pos), 
            limit,
            f"Should return at most {limit} results when limit={limit}"
        )
        
        # Validate each returned PO
        for po in pos:
            self.validate_purchase_order(po)

    def test_purchase_orders_have_valid_statuses(self):
        """Validate all POs have valid status values (non-empty strings)."""
        response = self.client.get("/purchase-orders")
        pos = self.validate_response_structure(response.json())
        pos = self.validate_non_empty_data(pos, "purchase order")
        
        # Check first 10 POs have non-empty string statuses
        for po in pos[:10]:
            self.assertIn("status", po, f"PO {po.get('name')} missing status field")
            self.assertIsInstance(po["status"], str, f"Status must be string for PO {po['name']}")
            self.assertGreater(len(po["status"]), 0, f"Status cannot be empty for PO {po['name']}")


class TestPurchaseOrderDetailIntegration(LocalIntegrationTestBase):
    """Integration tests for single purchase order endpoint against real ERPNext."""

    def test_purchase_order_detail_endpoint_returns_valid_data(self):
        """Validate detailed PO endpoint returns valid PO record with all fields."""
        # First, fetch a list to get a valid PO name
        list_response = self.client.get("/purchase-orders?limit=1")
        self.assertEqual(list_response.status_code, 200)
        
        pos = self.validate_response_structure(list_response.json())
        self.assertIsInstance(pos, list, "List response data must be a list")
        pos = self.validate_non_empty_data(pos, "purchase order")
        
        po_name = pos[0].get("name")
        self.assertIsNotNone(po_name, "PO name cannot be None")
        
        # Fetch detailed PO
        detail_response = self.client.get(f"/purchase-orders/{po_name}")
        self.assertEqual(detail_response.status_code, 200)
        
        po_data = self.validate_response_structure(detail_response.json())
        
        # Handle both dict and list responses
        if isinstance(po_data, dict):
            po_detail = po_data
        elif isinstance(po_data, list):
            po_detail = self.validate_non_empty_data(po_data, "purchase order detail")
            po_detail = po_detail[0]
        else:
            self.fail(f"Unexpected data type for PO detail: {type(po_data)}")
        
        # Validate detailed PO
        self.validate_purchase_order(po_detail)

    def test_purchase_order_detail_has_more_fields_than_list(self):
        """Validate detailed endpoint provides same or more information than list."""
        # Get list PO
        list_response = self.client.get("/purchase-orders?limit=1")
        list_pos = self.validate_response_structure(list_response.json())
        self.assertIsInstance(list_pos, list, "List response data must be a list")
        list_pos = self.validate_non_empty_data(list_pos, "purchase order")
        
        list_po = list_pos[0]
        po_name = list_po["name"]
        list_po_fields = set(list_po.keys())
        
        # Get detail PO
        detail_response = self.client.get(f"/purchase-orders/{po_name}")
        po_data = self.validate_response_structure(detail_response.json())
        
        # Handle both dict and list responses
        if isinstance(po_data, dict):
            detail_po = po_data
        elif isinstance(po_data, list):
            detail_po = self.validate_non_empty_data(po_data, "purchase order detail")
            detail_po = detail_po[0]
        else:
            self.fail(f"Unexpected data type for PO detail: {type(po_data)}")
        
        detail_po_fields = set(detail_po.keys())
        
        # Detail should have same or more fields than list
        self.assertTrue(
            detail_po_fields >= list_po_fields,
            f"Detail should have at least same fields as list. "
            f"Missing: {list_po_fields - detail_po_fields}"
        )


if __name__ == "__main__":
    unittest.main()
