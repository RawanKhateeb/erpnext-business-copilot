"""
Unit tests for intent recognition.
Tests all intent parsing logic without API calls.
"""

import unittest
from app.copilot.intent import parse_intent


class TestIntentParsing(unittest.TestCase):
    """Test intent.parse_intent() for all intents."""

    # ============ Risk Analysis ============
    def test_intent_analyze_po_risks_keyword_risk(self):
        """Test 'risk' keyword triggers analyze_po_risks."""
        result = parse_intent("What are the risks?")
        self.assertEqual(result["intent"], "analyze_po_risks")

    def test_intent_analyze_po_risks_keyword_risky(self):
        """Test 'risky' keyword triggers analyze_po_risks."""
        result = parse_intent("This order looks risky")
        self.assertEqual(result["intent"], "analyze_po_risks")

    def test_intent_analyze_po_risks_keyword_analyze_order(self):
        """Test 'analyze' + 'order' triggers analyze_po_risks."""
        result = parse_intent("Analyze purchase orders")
        self.assertEqual(result["intent"], "analyze_po_risks")

    def test_intent_analyze_po_risks_keyword_analyze_po(self):
        """Test 'analyze' + 'po' triggers analyze_po_risks."""
        result = parse_intent("Analyze PO risks")
        self.assertEqual(result["intent"], "analyze_po_risks")

    # ============ PO Approval ============
    def test_intent_approve_po_simple(self):
        """Test 'approve' keyword triggers approve_po."""
        result = parse_intent("Should I approve this?")
        self.assertEqual(result["intent"], "approve_po")

    def test_intent_approve_po_should_i_approve(self):
        """Test 'should i approve' triggers approve_po."""
        result = parse_intent("Should I approve PO-001?")
        self.assertEqual(result["intent"], "approve_po")

    def test_intent_approve_po_can_i_approve(self):
        """Test 'can i approve' triggers approve_po."""
        result = parse_intent("Can I approve this order?")
        self.assertEqual(result["intent"], "approve_po")

    def test_intent_approve_po_with_po_name(self):
        """Test approve_po extracts PO name."""
        result = parse_intent("Should I approve PUR-ORD-2026-00001?")
        self.assertEqual(result["intent"], "approve_po")
        self.assertEqual(result["po_name"], "PUR-ORD-2026-00001")

    def test_intent_approve_po_with_po_name_lowercase(self):
        """Test approve_po extracts PO name from lowercase input."""
        result = parse_intent("should i approve pur-ord-2026-00001?")
        self.assertEqual(result["po_name"], "PUR-ORD-2026-00001")

    # ============ Price Anomalies ============
    def test_intent_detect_price_anomalies_expensive(self):
        """Test 'expensive' keyword triggers detect_price_anomalies."""
        result = parse_intent("This is too expensive")
        self.assertEqual(result["intent"], "detect_price_anomalies")

    def test_intent_detect_price_anomalies_anomaly(self):
        """Test 'anomaly' keyword triggers detect_price_anomalies."""
        result = parse_intent("Find anomalies")
        self.assertEqual(result["intent"], "detect_price_anomalies")

    def test_intent_detect_price_anomalies_overpriced(self):
        """Test 'overpriced' keyword triggers detect_price_anomalies."""
        result = parse_intent("Are prices overpriced?")
        self.assertEqual(result["intent"], "detect_price_anomalies")

    def test_intent_detect_price_anomalies_unusual(self):
        """Test 'unusual' keyword triggers detect_price_anomalies."""
        result = parse_intent("Unusual prices")
        self.assertEqual(result["intent"], "detect_price_anomalies")

    def test_intent_detect_price_anomalies_price_check(self):
        """Test 'price' + 'check' triggers detect_price_anomalies."""
        result = parse_intent("Check prices")
        self.assertEqual(result["intent"], "detect_price_anomalies")

    # ============ Delayed Orders ============
    def test_intent_detect_delayed_orders_delay(self):
        """Test 'delay' keyword triggers detect_delayed_orders."""
        result = parse_intent("Are there delays?")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_intent_detect_delayed_orders_late(self):
        """Test 'late' keyword triggers detect_delayed_orders."""
        result = parse_intent("What's late?")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_intent_detect_delayed_orders_overdue(self):
        """Test 'overdue' keyword triggers detect_delayed_orders."""
        result = parse_intent("Show overdue orders")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_intent_detect_delayed_orders_past_due(self):
        """Test 'past due' keyword triggers detect_delayed_orders."""
        result = parse_intent("What's past due?")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_intent_detect_delayed_orders_slow_delivery(self):
        """Test 'slow' + 'delivery' triggers detect_delayed_orders."""
        result = parse_intent("Show slow delivery orders")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    def test_intent_detect_delayed_orders_behind_order(self):
        """Test 'behind' + 'order' triggers detect_delayed_orders."""
        result = parse_intent("Orders behind schedule")
        self.assertEqual(result["intent"], "detect_delayed_orders")

    # ============ Customer ============
    def test_intent_list_customers(self):
        """Test 'customer' keyword triggers list_customers."""
        result = parse_intent("Show customers")
        self.assertEqual(result["intent"], "list_customers")

    def test_intent_list_customers_all(self):
        """Test 'customer' priority over other keywords."""
        result = parse_intent("List all customers")
        self.assertEqual(result["intent"], "list_customers")

    # ============ Sales Order ============
    def test_intent_list_sales_orders_exact(self):
        """Test 'sales order' keyword triggers list_sales_orders."""
        result = parse_intent("Show sales orders")
        self.assertEqual(result["intent"], "list_sales_orders")

    def test_intent_list_sales_orders_so_keyword(self):
        """Test 'SO' keyword triggers list_sales_orders."""
        result = parse_intent("List SO")
        self.assertEqual(result["intent"], "list_sales_orders")

    # ============ Sales Invoice ============
    def test_intent_list_sales_invoices(self):
        """Test 'invoice' keyword triggers list_sales_invoices."""
        result = parse_intent("Show invoices")
        self.assertEqual(result["intent"], "list_sales_invoices")

    def test_intent_list_sales_invoices_exact(self):
        """Test 'sales invoice' keyword triggers list_sales_invoices."""
        result = parse_intent("Show sales invoices")
        self.assertEqual(result["intent"], "list_sales_invoices")

    # ============ Vendor Bills ============
    def test_intent_list_vendor_bills(self):
        """Test 'vendor bill' keyword triggers list_vendor_bills."""
        result = parse_intent("Show vendor bills")
        self.assertEqual(result["intent"], "list_vendor_bills")

    def test_intent_list_vendor_bills_bill_purchase(self):
        """Test 'bill' + 'purchase' keywords trigger list_vendor_bills."""
        result = parse_intent("Show purchase bills")
        self.assertEqual(result["intent"], "list_vendor_bills")

    # ============ Get PO by Name ============
    def test_intent_get_purchase_order_by_name(self):
        """Test PO name extraction for get_purchase_order."""
        result = parse_intent("Get PUR-ORD-2026-00001")
        self.assertEqual(result["intent"], "get_purchase_order")
        self.assertEqual(result["po_name"], "PUR-ORD-2026-00001")

    def test_intent_get_purchase_order_details(self):
        """Test details request with PO name."""
        result = parse_intent("Details for PUR-ORD-2026-00001")
        self.assertEqual(result["intent"], "get_purchase_order")
        self.assertEqual(result["po_name"], "PUR-ORD-2026-00001")

    # ============ Reports ============
    def test_intent_monthly_report_keyword(self):
        """Test 'monthly' + 'report' triggers monthly_report."""
        result = parse_intent("Generate monthly report")
        self.assertEqual(result["intent"], "monthly_report")

    def test_intent_monthly_report_spend(self):
        """Test 'monthly' + 'spend' triggers monthly_report."""
        result = parse_intent("Monthly spend report")
        self.assertEqual(result["intent"], "monthly_report")

    def test_intent_monthly_report_spend_only(self):
        """Test 'spend report' triggers monthly_report."""
        result = parse_intent("Show spend report")
        self.assertEqual(result["intent"], "monthly_report")

    def test_intent_pending_report(self):
        """Test 'pending' + 'report' triggers pending_report."""
        result = parse_intent("Show pending report")
        self.assertEqual(result["intent"], "pending_report")

    def test_intent_pending_report_order(self):
        """Test 'pending' + 'order' triggers pending_report."""
        result = parse_intent("Show pending orders")
        self.assertEqual(result["intent"], "pending_report")

    # ============ Items ============
    def test_intent_list_items(self):
        """Test 'item' keyword triggers list_items."""
        result = parse_intent("Show items")
        self.assertEqual(result["intent"], "list_items")

    # ============ Suppliers ============
    def test_intent_list_suppliers(self):
        """Test 'supplier' keyword triggers list_suppliers."""
        result = parse_intent("Show suppliers")
        self.assertEqual(result["intent"], "list_suppliers")

    # ============ Purchase Orders (Generic) ============
    def test_intent_list_purchase_orders_keyword(self):
        """Test 'purchase order' triggers list_purchase_orders."""
        result = parse_intent("Show purchase orders")
        self.assertEqual(result["intent"], "list_purchase_orders")

    def test_intent_list_purchase_orders_purchase(self):
        """Test 'purchase' keyword triggers list_purchase_orders."""
        result = parse_intent("Show purchases")
        self.assertEqual(result["intent"], "list_purchase_orders")

    def test_intent_list_purchase_orders_order(self):
        """Test 'order' keyword triggers list_purchase_orders."""
        result = parse_intent("Show all orders")
        self.assertEqual(result["intent"], "list_purchase_orders")

    # ============ Edge Cases ============
    def test_intent_empty_string(self):
        """Test empty string returns unknown intent."""
        result = parse_intent("")
        self.assertIn("intent", result)

    def test_intent_whitespace_only(self):
        """Test whitespace-only string."""
        result = parse_intent("   ")
        self.assertIn("intent", result)

    def test_intent_case_insensitive(self):
        """Test case insensitivity."""
        result1 = parse_intent("show suppliers")
        result2 = parse_intent("SHOW SUPPLIERS")
        result3 = parse_intent("Show Suppliers")
        self.assertEqual(result1["intent"], result2["intent"])
        self.assertEqual(result2["intent"], result3["intent"])

    def test_intent_priority_customer_over_order(self):
        """Test customer priority over generic order."""
        result = parse_intent("Customer orders")
        self.assertEqual(result["intent"], "list_customers")

    def test_intent_priority_sales_over_purchase(self):
        """Test sales order priority in ambiguous case."""
        result = parse_intent("Show sales order")
        self.assertEqual(result["intent"], "list_sales_orders")

    def test_intent_po_name_multiple_patterns(self):
        """Test PO name extraction with different formats."""
        po_name = "PUR-ORD-2024-00123"
        result = parse_intent(f"Approve {po_name}")
        self.assertEqual(result.get("po_name"), po_name)


if __name__ == "__main__":
    unittest.main()
