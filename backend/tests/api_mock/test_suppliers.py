"""
Unit tests for /suppliers endpoint.
Tests: list suppliers, response structure, error handling.
"""

import unittest
from unittest.mock import MagicMock, patch
from base_test import APITestBase
from mock_data import MOCK_SUPPLIERS


class TestSuppliersEndpoint(APITestBase):
    """Tests for /suppliers endpoint."""

    def test_suppliers_returns_200_with_data(self):
        """Happy path: suppliers endpoint returns 200 with supplier data."""
        # Mock the client
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.main.get_client', return_value=mock_client):
            response = self.client.get("/suppliers")

        self.assert_response_ok(response)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)

    def test_suppliers_response_has_expected_keys(self):
        """Verify supplier response has all expected fields."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.main.get_client', return_value=mock_client):
            response = self.client.get("/suppliers")

        data = response.json()
        supplier = data["data"][0]
        self.assert_json_keys(supplier, ["name", "supplier_name", "supplier_group"])

    def test_suppliers_returns_empty_list_when_no_suppliers(self):
        """Empty result: suppliers endpoint handles no data gracefully."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = []

        with patch('app.main.get_client', return_value=mock_client):
            response = self.client.get("/suppliers")

        self.assert_response_ok(response)
        data = response.json()
        self.assertEqual(len(data["data"]), 0)

    def test_suppliers_returns_500_on_client_error(self):
        """Error path: client exception results in 500."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("ERPNext connection failed")

        with patch('app.main.get_client', return_value=mock_client):
            response = self.client.get("/suppliers")

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())


class TestSuppliersData(unittest.TestCase):
    """Tests for supplier data structure."""

    def test_mock_suppliers_have_required_fields(self):
        """Mock data is properly structured."""
        for supplier in MOCK_SUPPLIERS:
            self.assertIn("name", supplier)
            self.assertIn("supplier_name", supplier)
            self.assertIn("country", supplier)


if __name__ == "__main__":
    unittest.main()
