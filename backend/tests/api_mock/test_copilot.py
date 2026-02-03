"""
Unittest-based API tests for copilot endpoint.
Tests the main POST /copilot/ask endpoint using FastAPI TestClient and unittest.mock.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class TestCopilotEndpoint(unittest.TestCase):
    """Test copilot endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    # ============ POST /copilot/ask ============
    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_list_suppliers(self, mock_erpnext_client):
        """Test POST /copilot/ask with list_suppliers intent."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = [
            {"name": "Supplier A", "supplier_name": "Supplier A"}
        ]
        mock_erpnext_client.return_value = mock_client

        response = self.client.post(
            "/copilot/ask",
            json={"query": "Show me all suppliers"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("intent", data)
        self.assertIn("answer", data)
        self.assertIn("data", data)
        self.assertEqual(data["intent"], "list_suppliers")

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_list_purchase_orders(self, mock_erpnext_client):
        """Test POST /copilot/ask with list_purchase_orders intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000}
        ]
        mock_erpnext_client.return_value = mock_client

        with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
            mock_insights.return_value = {
                "total_spend": 5000,
                "total_spend_formatted": "$5,000.00",
            }
            response = self.client.post(
                "/copilot/ask",
                json={"query": "Show purchase orders"}
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "list_purchase_orders")
        self.assertIn("answer", data)

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_total_spend(self, mock_erpnext_client):
        """Test POST /copilot/ask with total_spend intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "grand_total": 5000},
            {"name": "PO-002", "grand_total": 3000},
        ]
        mock_erpnext_client.return_value = mock_client

        with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
            mock_insights.return_value = {
                "total_spend": 8000,
                "total_spend_formatted": "$8,000.00",
                "average_order_value": 4000,
                "average_order_value_formatted": "$4,000.00"
            }
            response = self.client.post(
                "/copilot/ask",
                json={"query": "What's the total spend?"}
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "total_spend")
        self.assertIn("$8,000.00", data["answer"])

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_detect_delayed_orders(self, mock_erpnext_client):
        """Test POST /copilot/ask with detect_delayed_orders intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "status": "Pending", "transaction_date": "2024-01-01"}
        ]
        mock_erpnext_client.return_value = mock_client

        response = self.client.post(
            "/copilot/ask",
            json={"query": "Show delayed orders"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "detect_delayed_orders")

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_detect_price_anomalies(self, mock_erpnext_client):
        """Test POST /copilot/ask with detect_price_anomalies intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "item_code": "ITEM-1", "rate": 100, "qty": 10}
        ]
        mock_erpnext_client.return_value = mock_client

        response = self.client.post(
            "/copilot/ask",
            json={"query": "Find price anomalies"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "detect_price_anomalies")

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_analyze_po_risks(self, mock_erpnext_client):
        """Test POST /copilot/ask with analyze_po_risks intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000}
        ]
        mock_erpnext_client.return_value = mock_client

        response = self.client.post(
            "/copilot/ask",
            json={"query": "Analyze PO risks"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "analyze_po_risks")

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_approve_po(self, mock_erpnext_client):
        """Test POST /copilot/ask with approve_po intent."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = {
            "name": "PO-001",
            "supplier": "Supplier A",
            "grand_total": 5000
        }
        mock_erpnext_client.return_value = mock_client

        with patch('app.copilot.service.analyze_po_approval') as mock_analyze:
            mock_analyze.return_value = {
                "decision": "APPROVE",
                "summary": "Order looks good"
            }
            response = self.client.post(
                "/copilot/ask",
                json={"query": "Should I approve PO-001?"}
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "approve_po")

    def test_copilot_ask_empty_query(self):
        """Test POST /copilot/ask with empty query."""
        response = self.client.post(
            "/copilot/ask",
            json={"query": ""}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "unknown")

    def test_copilot_ask_missing_query_parameter(self):
        """Test POST /copilot/ask with missing query parameter."""
        response = self.client.post(
            "/copilot/ask",
            json={}
        )

        # Should return 422 (Unprocessable Entity) for missing required field
        self.assertEqual(response.status_code, 422)

    @patch('app.copilot.service.ERPNextClient')
    def test_copilot_ask_erp_connection_error(self, mock_erpnext_client):
        """Test POST /copilot/ask handles ERP connection errors."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("Connection failed")
        mock_erpnext_client.return_value = mock_client

        response = self.client.post(
            "/copilot/ask",
            json={"query": "Show suppliers"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)

    def test_copilot_ask_response_structure(self):
        """Test POST /copilot/ask response has required fields."""
        with patch('app.copilot.service.ERPNextClient') as mock_erpnext_client:
            mock_client = MagicMock()
            mock_client.list_suppliers.return_value = []
            mock_erpnext_client.return_value = mock_client

            response = self.client.post(
                "/copilot/ask",
                json={"query": "Show suppliers"}
            )

        data = response.json()
        required_keys = ["intent", "answer", "data", "insights", "next_questions"]
        for key in required_keys:
            self.assertIn(key, data, f"Missing required key: {key}")


if __name__ == "__main__":
    unittest.main()
