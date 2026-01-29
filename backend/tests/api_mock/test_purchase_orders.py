"""
Unit tests for /purchase-orders endpoint.
Tests: list POs, response structure, limit parameter, error handling.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.base_test import APITestBase
from backend.tests.api_mock.mock_data import MOCK_PURCHASE_ORDERS, MOCK_PURCHASE_ORDER_DETAIL


class TestPurchaseOrdersEndpoint(APITestBase):
    """Tests for /purchase-orders endpoint."""

    def test_purchase_orders_returns_200_with_data(self):
        """Happy path: POs endpoint returns 200 with data."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders")

        self.assert_response_ok(response)
        data = response.json()
        self.assertIn("data", data)
        self.assertEqual(len(data["data"]), 3)

    def test_purchase_orders_response_has_expected_keys(self):
        """Verify PO response has all expected fields."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders")

        data = response.json()
        po = data["data"][0]
        self.assert_json_keys(
            po, ["name", "supplier", "grand_total", "status", "transaction_date"]
        )

    def test_purchase_orders_respects_limit_parameter(self):
        """Parameter handling: limit parameter is passed to client."""
        mock_client = MagicMock()
        limited_pos = MOCK_PURCHASE_ORDERS[:2]
        mock_client.list_purchase_orders.return_value = limited_pos

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders?limit=2")

        mock_client.list_purchase_orders.assert_called_with(2)
        data = response.json()
        self.assertEqual(len(data["data"]), 2)

    def test_purchase_orders_default_limit(self):
        """Default limit is applied."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders")

        mock_client.list_purchase_orders.assert_called_with(20)

    def test_purchase_orders_returns_500_on_error(self):
        """Error path: client exception results in 500."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.side_effect = Exception("Database error")

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders")

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())


class TestPurchaseOrderDetailEndpoint(APITestBase):
    """Tests for /purchase-orders/{po_name} endpoint."""

    def test_purchase_order_detail_returns_200(self):
        """Happy path: PO detail returns 200 with data."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = MOCK_PURCHASE_ORDER_DETAIL

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders/PO-2024-001")

        self.assert_response_ok(response)
        data = response.json()
        self.assertIn("data", data)

    def test_purchase_order_detail_has_expected_keys(self):
        """Verify PO detail response has all expected fields."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = MOCK_PURCHASE_ORDER_DETAIL

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders/PO-2024-001")

        data = response.json()["data"]
        self.assert_json_keys(data, ["name", "supplier", "grand_total", "items"])

    def test_purchase_order_detail_calls_correct_po_name(self):
        """Parameter passing: correct PO name is passed."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = MOCK_PURCHASE_ORDER_DETAIL

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders/PO-2024-001")

        mock_client.get_purchase_order.assert_called_with("PO-2024-001")

    def test_purchase_order_detail_returns_500_on_error(self):
        """Error path: client exception results in 500."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.side_effect = Exception("PO not found")

        with patch('app.controllers.data.get_client', return_value=mock_client):
            response = self.client.get("/purchase-orders/INVALID")

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
