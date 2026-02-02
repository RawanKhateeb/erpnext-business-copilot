"""
Essential critical path tests for core business workflows.
Covers: approve_po, ai report endpoints, error handling, multi-intent flows.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.base_test import APITestBase
from app.copilot.service import handle_user_input

class TestCriticalPaths(unittest.TestCase):
    """Critical paths for reaching 90% coverage."""

    def test_approve_po_intent_with_po_name(self):
        """Test approve_po intent with valid PO name - calls analyze_po_approval."""
        mock_client = MagicMock()
        mock_po_data = {
            "name": "PUR-ORD-2026-00001",
            "supplier": "Supplier A",
            "grand_total": 5000,
            "status": "Draft"
        }
        mock_client.get_purchase_order.return_value = mock_po_data

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.analyze_po_approval') as mock_analyze:
                mock_analyze.return_value = {
                    "decision": "APPROVE",
                    "summary": "Order is within budget",
                    "findings": ["Good price", "Reliable supplier"],
                    "evidence": [{"type": "price", "value": "5000"}],
                    "next_actions": ["Submit PO"],
                    "po_data": mock_po_data,
                }
                
                # Extract PO name from text
                result = handle_user_input("Should I approve PUR-ORD-2026-00001?")

        # Verify approve_po intent was triggered
        self.assertEqual(result["intent"], "approve_po")
        self.assertIn("Approval Analysis", result["answer"])
        self.assertIn("APPROVE", result["answer"])
        self.assertIn("summary", result)
        self.assertIn("findings", result)
        self.assertIn("evidence", result)

    def test_approve_po_intent_without_po_name(self):
        """Test approve_po intent without PO name - shows help message."""
        mock_client = MagicMock()

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Should I approve this order?")

        # Should trigger approve_po but with no PO name
        self.assertEqual(result["intent"], "approve_po")
        self.assertIn("Please specify", result["answer"])
        self.assertIn("PUR-ORD", result["answer"])




class TestAICriticalPaths(APITestBase):
    """Critical paths in AI controller for 90% coverage."""

    def test_ai_report_endpoint_no_pos_available(self):
        """Test AI report endpoint when no POs available - error path."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = []  # Empty list

        with patch('app.controllers.ai.ERPNextClient', return_value=mock_client):
            response = self.client.post(
                "/ai/report",
                json={"query": "Generate report", "period": "month"}
            )

        # Should return 200 but with success=False
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("No purchase order", data.get("message", ""))

    def test_ai_report_endpoint_erp_connection_error(self):
        """Test AI report endpoint when ERPNext connection fails."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.side_effect = Exception("Connection failed")

        with patch('app.controllers.ai.ERPNextClient', return_value=mock_client):
            response = self.client.post(
                "/ai/report",
                json={"query": "Generate report", "period": "month"}
            )

        # Should return 200 but with error/failure status
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))
        # Either has "message" or "error" field indicating problem
        self.assertTrue("message" in data or "error" in data)

    def test_monthly_report_comprehensive(self):
        """Test comprehensive monthly report generation."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "transaction_date": "2024-01-15", "grand_total": 5000}
        ]
        mock_client.list_sales_invoices.return_value = [
            {"name": "INV-001", "posting_date": "2024-01-10", "grand_total": 3000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Generate comprehensive monthly report")

        self.assertEqual(result["intent"], "monthly_report")
        self.assertIn("answer", result)

    def test_pending_report_generation(self):
        """Test pending items/orders report."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "status": "Pending"}
        ]
        mock_client.list_sales_invoices.return_value = []

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Generate pending report")

        self.assertEqual(result["intent"], "pending_report")
        self.assertIn("answer", result)

    def test_complete_flow_with_multiple_intents(self):
        """Test complete flow with multiple consecutive intent requests."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = [
            {"name": "SUP-001", "supplier_name": "Supplier A"}
        ]
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "SUP-001", "grand_total": 5000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            # Flow: ask for suppliers -> POs
            result1 = handle_user_input("Show suppliers")
            self.assertEqual(result1["intent"], "list_suppliers")

            result2 = handle_user_input("Now show purchase orders")
            self.assertEqual(result2["intent"], "list_purchase_orders")

    def test_empty_pos_list(self):
        """Test handling when PO list is empty."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = []

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Generate monthly report")

        # Should handle gracefully
        self.assertEqual(result["intent"], "monthly_report")
        self.assertIn("answer", result)

    def test_items_retrieval(self):
        """Test listing items."""
        mock_client = MagicMock()
        mock_client.list_items.return_value = [
            {"name": "ITEM-001", "item_name": "Item 1"},
            {"name": "ITEM-002", "item_name": "Item 2"}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show items")

        self.assertEqual(result["intent"], "list_items")
        self.assertIn("data", result)

    def test_get_purchase_order_by_name(self):
        """Test retrieving specific purchase order by name."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = {
            "name": "PUR-ORD-2026-00001",
            "supplier": "Supplier A",
            "grand_total": 5000,
            "status": "Pending"
        }

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Get PUR-ORD-2026-00001")

        self.assertEqual(result["intent"], "get_purchase_order")
        self.assertIn("data", result)

    def test_list_sales_orders(self):
        """Test listing sales orders."""
        mock_client = MagicMock()
        mock_client.list_sales_orders.return_value = [
            {"name": "SO-001", "customer": "Customer A", "grand_total": 3000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show sales orders")

        self.assertEqual(result["intent"], "list_sales_orders")
        self.assertIn("data", result)


if __name__ == "__main__":
    unittest.main()
