"""
Integration tests for service.handle_user_input() - Tests core copilot logic.
Purpose: Exercise service helpers and intent parsing with real mock data.
Strategy: Call handle_user_input() with different intents to trigger code paths.
"""

import unittest
from unittest.mock import MagicMock, patch
from backend.tests.api_mock.mock_data import MOCK_SUPPLIERS, MOCK_PURCHASE_ORDERS, MOCK_ITEMS
from app.copilot.service import handle_user_input


class TestServiceIntegration(unittest.TestCase):
    """Integration tests for service.handle_user_input()."""

    def test_list_suppliers_intent(self):
        """Test list_suppliers intent - exercises helper functions."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Verify intent recognized
        self.assertEqual(result["intent"], "list_suppliers")
        
        # Verify response structure
        self.assertIn("answer", result)
        self.assertIn("data", result)
        self.assertIn("insights", result)
        self.assertIn("next_questions", result)
        
        # Verify data is suppliers list
        self.assertEqual(len(result["data"]), 3)
        self.assertEqual(result["data"][0]["name"], "Supplier A")

    def test_list_purchase_orders_intent(self):
        """Test list_purchase_orders intent - exercises PO metrics calculation."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 15700.00,
                    "total_spend_formatted": "$15,700.00",
                    "average_order_value": 5233.33,
                    "average_order_value_formatted": "$5,233.33",
                    "recommendations": ["Consolidate with top suppliers"]
                }
                
                result = handle_user_input("Show purchase orders")

        # Verify intent
        self.assertEqual(result["intent"], "list_purchase_orders")
        
        # Verify structure
        self.assertIn("answer", result)
        self.assertIn("data", result)
        self.assertIn("insights", result)
        self.assertIn("metrics", result)
        
        # Verify metrics were calculated
        self.assertEqual(len(result["data"]), 3)

    def test_total_spend_intent(self):
        """Test total_spend intent - exercises spend calculation helpers."""
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

        # Verify response
        self.assertEqual(result["intent"], "total_spend")
        self.assertIn("$15,700.00", result["answer"])
        
        # Verify metrics included
        self.assertIn("metrics", result)

    def test_empty_input_handling(self):
        """Test empty/invalid input - exercises error handling."""
        result = handle_user_input("")
        
        self.assertEqual(result["intent"], "unknown")
        self.assertIn("Please provide", result["answer"])
        self.assertIsInstance(result["insights"], list)
        self.assertIsInstance(result["next_questions"], list)

    def test_invalid_input_type_handling(self):
        """Test non-string input - exercises type validation."""
        result = handle_user_input(None)
        
        self.assertEqual(result["intent"], "unknown")
        self.assertIn("Please provide", result["answer"])

    def test_detect_delayed_orders_intent(self):
        """Test detect_delayed_orders intent - exercises delayed order detection."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show me delayed orders")

        # Verify intent recognized
        self.assertEqual(result["intent"], "detect_delayed_orders")
        self.assertIn("answer", result)
        self.assertIn("data", result)

    def test_detect_price_anomalies_intent(self):
        """Test detect_price_anomalies intent - exercises price analysis."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Are there price anomalies?")

        # Verify intent recognized
        self.assertEqual(result["intent"], "detect_price_anomalies")
        self.assertIn("answer", result)

    def test_list_customers_intent(self):
        """Test list_customers intent - exercises customer data retrieval."""
        mock_client = MagicMock()
        mock_client.list_customers.return_value = [
            {"name": "Customer 1", "outstanding_amount": 5000},
            {"name": "Customer 2", "outstanding_amount": 3000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show customers")

        # Verify intent recognized
        self.assertEqual(result["intent"], "list_customers")
        self.assertIn("answer", result)
        self.assertIn("data", result)

    def test_list_sales_invoices_intent(self):
        """Test list_sales_invoices intent."""
        mock_client = MagicMock()
        mock_client.list_sales_invoices.return_value = [
            {"name": "INV-001", "customer": "Customer 1", "grand_total": 5000},
            {"name": "INV-002", "customer": "Customer 2", "grand_total": 3000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show sales invoices")

        # Verify intent recognized
        self.assertEqual(result["intent"], "list_sales_invoices")
        self.assertIn("data", result)

    def test_monthly_report_intent(self):
        """Test monthly_report intent - exercises monthly metrics."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS
        mock_client.list_sales_invoices.return_value = [
            {"name": "INV-001", "posting_date": "2024-01-15", "grand_total": 5000}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Generate monthly report")

        # Verify intent recognized
        self.assertEqual(result["intent"], "monthly_report")
        self.assertIn("answer", result)

    def test_list_vendor_bills_intent(self):
        """Test list_vendor_bills intent."""
        mock_client = MagicMock()
        mock_client.list_vendor_bills.return_value = [
            {"name": "BILL-001", "supplier": "Supplier A", "grand_total": 2000},
            {"name": "BILL-002", "supplier": "Supplier B", "grand_total": 1500}
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show vendor bills")

        # Verify intent recognized
        self.assertEqual(result["intent"], "list_vendor_bills")
        self.assertIn("data", result)

    def test_erp_connection_error_handling(self):
        """Test ERPNext connection error - exercises error path."""
        mock_client = MagicMock()
        mock_client.list_suppliers.side_effect = Exception("Connection failed")

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Should still return response with error message
        self.assertEqual(result["intent"], "list_suppliers")
        self.assertIn("answer", result)
        self.assertIn("occurred", result["answer"])

    def test_analyze_po_risks_intent(self):
        """Test analyze_po_risks intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Analyze PO risks")

        # Verify intent recognized
        self.assertEqual(result["intent"], "analyze_po_risks")
        self.assertIn("answer", result)

    def test_pending_report_intent(self):
        """Test pending_report intent."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS
        mock_client.list_sales_invoices.return_value = []

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Generate pending report")

        # Verify intent recognized
        self.assertEqual(result["intent"], "pending_report")
        self.assertIn("answer", result)

    def test_approve_po_with_name_intent(self):
        """Test approve_po intent with PO name."""
        mock_client = MagicMock()
        mock_client.approve_po.return_value = {"status": "success"}

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Approve PO-001")

        # Verify intent recognized
        self.assertEqual(result["intent"], "approve_po")
        self.assertIn("answer", result)

    def test_approve_po_without_name_intent(self):
        """Test approve_po intent without PO name."""
        result = handle_user_input("Approve the purchase order")

        # Should recognize approve_po intent
        self.assertEqual(result["intent"], "approve_po")
        self.assertIn("answer", result)

    def test_text_with_date_extraction(self):
        """Test intent detection with date references."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show me purchase orders from this month")

        # Should recognize the intent and extract date
        self.assertIn("intent", result)
        self.assertIn("answer", result)

    def test_complex_business_query(self):
        """Test handling of complex business queries."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 15700.00,
                    "total_spend_formatted": "$15,700.00",
                    "average_order_value": 5233.33,
                    "average_order_value_formatted": "$5,233.33"
                }
                
                result = handle_user_input("What are my top suppliers by spend this month?")

        # Should provide meaningful response
        self.assertIn("intent", result)
        self.assertIn("answer", result)
        self.assertIn("data", result)

    def test_various_intent_phrasings(self):
        """Test multiple phrasings for same intent."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        # Test multiple phrasings for list_suppliers
        phrasings = [
            "Give me suppliers",
            "Show suppliers",
            "List all suppliers"
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            for phrase in phrasings:
                result = handle_user_input(phrase)
                self.assertEqual(result["intent"], "list_suppliers", f"Failed for phrase: {phrase}")

    def test_all_intents_have_response(self):
        """Test that each intent gets a proper response structure."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS
        mock_client.list_customers.return_value = []
        mock_client.list_sales_invoices.return_value = []
        mock_client.list_vendor_bills.return_value = []
        mock_client.approve_po.return_value = {"status": "success"}

        intent_queries = [
            "list_suppliers",
            "list_purchase_orders", 
            "total_spend",
            "approve_po",
            "detect_delayed_orders",
            "detect_price_anomalies",
            "analyze_po_risks",
            "list_customers",
            "list_sales_invoices",
            "list_vendor_bills",
            "monthly_report"
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            for query in intent_queries:
                result = handle_user_input(query)
                # All should have these keys
                self.assertIn("intent", result)
                self.assertIn("answer", result)
                self.assertIn("data", result)
                self.assertIn("next_questions", result)

    def test_po_approval_full_flow(self):
        """Test full approval flow with different inputs."""
        mock_client = MagicMock()
        mock_client.approve_po.return_value = {"status": "success", "name": "PO-001"}

        test_cases = [
            "Approve PO-001",
            "Approve po-002", 
            "Approve purchase order PO-123"
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            for query in test_cases:
                result = handle_user_input(query)
                self.assertEqual(result["intent"], "approve_po")

    def test_response_formatting_completeness(self):
        """Test that all response fields are properly formatted."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Verify all required keys exist
        required_keys = ["intent", "answer", "data", "insights", "next_questions"]
        for key in required_keys:
            self.assertIn(key, result, f"Missing required key: {key}")

        # Verify types
        self.assertIsInstance(result["intent"], str)
        self.assertIsInstance(result["answer"], str)
        self.assertIsInstance(result["data"], (list, dict))
        self.assertIsInstance(result["insights"], list)
        self.assertIsInstance(result["next_questions"], list)

    def test_insights_generation(self):
        """Test that insights are properly generated."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = MOCK_PURCHASE_ORDERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            with patch('app.copilot.service.build_purchase_order_insights') as mock_insights:
                mock_insights.return_value = {
                    "total_spend": 15700.00,
                    "total_spend_formatted": "$15,700.00",
                    "average_order_value": 5233.33,
                    "average_order_value_formatted": "$5,233.33",
                    "recommendations": ["Consolidate suppliers"]
                }
                
                result = handle_user_input("Show purchase orders")

        # Verify insights are included
        self.assertIn("insights", result)
        self.assertIsInstance(result["insights"], list)

    def test_empty_supplier_list_handling(self):
        """Test handling of empty supplier list."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = []

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Should handle empty gracefully
        self.assertEqual(result["intent"], "list_suppliers")
        self.assertIn("answer", result)
        self.assertEqual(result["data"], [])

    def test_empty_po_list_handling(self):
        """Test handling of empty purchase orders."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = []

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show purchase orders")

        # Should handle empty gracefully
        self.assertEqual(result["intent"], "list_purchase_orders")
        self.assertEqual(result["data"], [])

    def test_special_characters_in_query(self):
        """Test handling of special characters in user input."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            # Test various special characters that might be in input
            result = handle_user_input("Show suppliers!!! @@@ ###")

        # Should process even with special chars
        self.assertIn("intent", result)
        self.assertIn("answer", result)

    def test_case_insensitive_intent_recognition(self):
        """Test that intent recognition is case insensitive."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        test_queries = [
            "SHOW SUPPLIERS",
            "Show Suppliers",
            "show suppliers",
            "ShOw SuPpLiErS"
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            for query in test_queries:
                result = handle_user_input(query)
                self.assertEqual(result["intent"], "list_suppliers", f"Failed for query: {query}")

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled properly."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        test_queries = [
            "   Show suppliers   ",
            "Show   suppliers",
            "Show suppliers  ",
            "\tShow suppliers"
        ]

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            for query in test_queries:
                result = handle_user_input(query)
                self.assertEqual(result["intent"], "list_suppliers", f"Failed for query: {repr(query)}")

    def test_next_questions_suggestions(self):
        """Test that next_questions are provided as suggestions."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            result = handle_user_input("Show suppliers")

        # Should have next questions for guidance
        self.assertIn("next_questions", result)
        self.assertIsInstance(result["next_questions"], list)
        self.assertGreater(len(result["next_questions"]), 0)

    def test_response_consistency(self):
        """Test that responses maintain consistent structure."""
        mock_client = MagicMock()
        mock_client.list_suppliers.return_value = MOCK_SUPPLIERS

        with patch('app.copilot.service.ERPNextClient', return_value=mock_client):
            # Call same intent twice
            result1 = handle_user_input("Show suppliers")
            result2 = handle_user_input("Show suppliers")

        # Both should have same structure
        self.assertEqual(set(result1.keys()), set(result2.keys()))
        self.assertEqual(result1["intent"], result2["intent"])


if __name__ == "__main__":
    unittest.main()
