"""
Critical coverage tests for 90% target.
Focuses on high-impact missing paths: approve_po intent and ai error paths.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.base_test import APITestBase
from app.copilot.service import handle_user_input

class TestIntentResponseStructure(unittest.TestCase):
    """Test that all intents return proper response structures."""

    def test_delayed_orders_detection_response(self):
        """Test delayed orders detection returns proper structure."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "transaction_date": "2024-01-01", "status": "Pending"}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Detect delayed orders")

        self.assertEqual(result["intent"], "detect_delayed_orders")
        self.assertIn("answer", result)
        self.assertIn("data", result)

    def test_price_anomalies_response(self):
        """Test price anomalies detection response."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "item_code": "ITEM-1", "rate": 100, "qty": 10}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Find price anomalies")

        self.assertEqual(result["intent"], "detect_price_anomalies")
        self.assertIn("answer", result)

    def test_risk_analysis_response(self):
        """Test PO risk analysis response."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Analyze risks in purchase orders")

        self.assertEqual(result["intent"], "analyze_po_risks")
        self.assertIn("answer", result)

    def test_customer_list_response_structure(self):
        """Test customers list response structure."""
        mock_client = MagicMock()
        mock_client.list_customers.return_value = [
            {"name": "CUST-001", "customer_name": "Customer One"}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("List customers")

        self.assertEqual(result["intent"], "list_customers")
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)

    def test_vendor_bills_response(self):
        """Test vendor bills response."""
        mock_client = MagicMock()
        mock_client.list_vendor_bills.return_value = [
            {"name": "BILL-001", "supplier": "Supplier A"}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show vendor bills")

        self.assertEqual(result["intent"], "list_vendor_bills")
        self.assertIn("answer", result)

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

    def test_list_sales_invoices_intent(self):
        """Test list_sales_invoices intent - covers unpaid receivables path."""
        mock_client = MagicMock()
        mock_client.list_sales_invoices.return_value = [
            {
                "name": "SI-001",
                "customer": "Customer A",
                "outstanding_amount": 5000,
                "status": "Overdue"
            },
            {
                "name": "SI-002",
                "customer": "Customer B",
                "outstanding_amount": 0,
                "status": "Paid"
            },
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show sales invoices")

        # Verify sales invoices were listed
        self.assertEqual(result["intent"], "list_sales_invoices")
        self.assertIn("2", result["answer"])  # 2 invoices
        self.assertIn("$5,000.00", result["answer"])  # Outstanding amount formatted
        self.assertIn("Outstanding", result["answer"])
        self.assertEqual(len(result["data"]), 2)


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

    def test_erp_error_handling_complete(self):
        """Test complete error handling with various exception types."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.side_effect = ValueError("Invalid data")

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show purchase orders")

        self.assertEqual(result["intent"], "list_purchase_orders")
        self.assertIn("answer", result)

    def test_get_po_with_detailed_insights(self):
        """Test PO retrieval with full insights."""
        mock_client = MagicMock()
        mock_client.get_purchase_order.return_value = {
            "name": "PUR-ORD-2026-00001",
            "supplier": "Supplier A",
            "grand_total": 5000,
            "status": "Submitted",
            "items": [{"item_code": "ITEM-1", "qty": 10, "rate": 500}]
        }

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Details for PUR-ORD-2026-00001")

        self.assertEqual(result["intent"], "get_purchase_order")
        self.assertIn("insights", result)

    def test_sales_invoices_with_metrics(self):
        """Test sales invoice retrieval with metrics."""
        mock_client = MagicMock()
        mock_client.list_sales_invoices.return_value = [
            {"name": "INV-001", "customer": "Customer A", "grand_total": 5000, "outstanding_amount": 0},
            {"name": "INV-002", "customer": "Customer B", "grand_total": 3000, "outstanding_amount": 1500}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("List sales invoices")

        self.assertEqual(result["intent"], "list_sales_invoices")
        self.assertEqual(len(result["data"]), 2)

    def test_comprehensive_purchase_order_analysis(self):
        """Test comprehensive PO analysis with multiple statuses."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "status": "Draft", "grand_total": 1000},
            {"name": "PO-002", "status": "Submitted", "grand_total": 2000},
            {"name": "PO-003", "status": "Completed", "grand_total": 3000},
            {"name": "PO-004", "status": "Cancelled", "grand_total": 500}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 6000,
                    "total_spend_formatted": "$6,000.00",
                    "average_order_value": 1500,
                    "average_order_value_formatted": "$1,500.00"
                }
                
                result = handle_user_input("Analyze all purchase orders")

        self.assertIn("intent", result)
        self.assertIn("answer", result)

    def test_vendor_bills_with_outstanding(self):
        """Test vendor bills with outstanding amounts."""
        mock_client = MagicMock()
        mock_client.list_vendor_bills.return_value = [
            {"name": "BILL-001", "supplier": "Supplier A", "grand_total": 2000, "outstanding_amount": 2000},
            {"name": "BILL-002", "supplier": "Supplier B", "grand_total": 1500, "outstanding_amount": 0}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show vendor bills with outstanding")

        self.assertEqual(result["intent"], "list_vendor_bills")
        self.assertGreater(len(result["data"]), 0)

    def test_customers_with_outstanding(self):
        """Test customers list with outstanding amounts."""
        mock_client = MagicMock()
        mock_client.list_customers.return_value = [
            {"name": "CUST-001", "customer_name": "Customer A", "outstanding_amount": 5000},
            {"name": "CUST-002", "customer_name": "Customer B", "outstanding_amount": 0}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("List customers with outstanding")

        self.assertEqual(result["intent"], "list_customers")
        self.assertEqual(len(result["data"]), 2)


if __name__ == "__main__":
    unittest.main()
