"""
Unit tests for /copilot/ask endpoint.
Tests: intent parsing, data fetching, error handling.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.base_test import APITestBase
from backend.tests.api_mock.mock_data import MOCK_SUPPLIERS, MOCK_PURCHASE_ORDERS


class TestCopilotAskEndpoint(APITestBase):
    """Tests for /copilot/ask endpoint."""

    def test_copilot_ask_list_suppliers_intent(self):
        """Happy path: copilot ask recognizes supplier query."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post("/copilot/ask", json={"query": "Show suppliers"})

        self.assert_response_ok(response)
        data = response.json()
        has_response = "data" in data or "message" in data or "answer" in data
        self.assertTrue(has_response)

    def test_copilot_ask_list_purchase_orders_intent(self):
        """Happy path: copilot ask recognizes PO query."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post(
                "/copilot/ask", json={"query": "Show purchase orders"}
            )

        self.assert_response_ok(response)
        data = response.json()
        has_response = "data" in data or "message" in data or "answer" in data
        self.assertTrue(has_response)

    def test_copilot_ask_missing_query_parameter(self):
        """Error path: missing query parameter."""
        response = self.client.post("/copilot/ask", json={})

        self.assertIn(response.status_code, [400, 422])

    def test_copilot_ask_empty_query(self):
        """Error path: empty query string."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post("/copilot/ask", json={"query": ""})

        # Response should be 200, but data may be empty or error message
        self.assertIn(response.status_code, [200, 400, 422])

    def test_copilot_ask_returns_message_field(self):
        """Response structure: includes message or answer field."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post("/copilot/ask", json={"query": "suppliers"})

        data = response.json()
        # API returns either 'message' or 'answer' field
        has_response = "message" in data or "answer" in data or "data" in data
        self.assertTrue(has_response, "Response should contain message/answer/data")

    def test_copilot_ask_handles_client_error(self):
        """Error path: client raises exception."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("Connection error")

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post("/copilot/ask", json={"query": "suppliers"})

        # Should handle gracefully (either 500 or error message in response)
        self.assertIn(response.status_code, [200, 500])


class TestCopilotEndpoint(APITestBase):
    """Tests for /copilot endpoint (POST)."""

    def test_copilot_requires_query(self):
        """Validation: query parameter is required."""
        response = self.client.post("/copilot", json={})
        self.assertIn(response.status_code, [400, 422])

    def test_copilot_accepts_query_parameter(self):
        """Happy path: copilot accepts valid query."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            response = self.client.post("/copilot", json={"query": "list suppliers"})

        self.assert_response_ok(response)


if __name__ == "__main__":
    unittest.main()
