"""
Integration tests for service.handle_user_input() - Core business logic tests.
Essential tests for 8 key business skills/intents.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.mock_data import MOCK_SUPPLIERS, MOCK_PURCHASE_ORDERS
from app.copilot.service import handle_user_input


class TestServiceIntegration(unittest.TestCase):
    """Core integration tests for handle_user_input() - 8 essential skills."""

    def test_list_suppliers_intent(self):
        """Test list_suppliers intent."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        self.assertEqual(result["intent"], "list_suppliers")
        self.assertIn("answer", result)
        self.assertEqual(len(result["data"]), 3)

    def test_list_purchase_orders_intent(self):
        """Test list_purchase_orders intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 15700.00,
                    "total_spend_formatted": "$15,700.00",
                }
                result = handle_user_input("Show purchase orders")

        self.assertEqual(result["intent"], "list_purchase_orders")
        self.assertIn("metrics", result)

    def test_total_spend_intent(self):
        """Test total_spend calculation."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 15700.00,
                    "total_spend_formatted": "$15,700.00",
                    "average_order_value": 5233.33,
                    "average_order_value_formatted": "$5,233.33"
                }
                result = handle_user_input("What's the total spend?")

        self.assertEqual(result["intent"], "total_spend")
        self.assertIn("$15,700.00", result["answer"])

    def test_detect_delayed_orders_intent(self):
        """Test delayed order detection."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show me delayed orders")

        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_detect_price_anomalies_intent(self):
        """Test price anomaly detection."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Are there price anomalies?")

        self.assertEqual(result["intent"], "detect_price_anomalies")

    def test_analyze_po_risks_intent(self):
        """Test PO risk analysis."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Analyze PO risks")

        self.assertEqual(result["intent"], "analyze_po_risks")

    def test_approve_po_intent(self):
        """Test approve PO with name."""
        mock_client = MagicMock()

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Approve PO-001")

        self.assertEqual(result["intent"], "approve_po")

    def test_error_handling_on_connection_failure(self):
        """Test error handling on ERP connection failure."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("Connection failed")

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Should still return valid response structure despite error
        self.assertIn("answer", result)
        self.assertIn("intent", result)


if __name__ == "__main__":
    unittest.main()
