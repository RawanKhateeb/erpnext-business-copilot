"""
Unit tests for service functions.
Tests detector and analyzer logic without API calls.
"""

import unittest
from app.services.price_anomaly_detector import detect_price_anomalies
from app.services.delayed_orders_detector import detect_delayed_orders
from app.services.po_risk_analyzer import analyze_po_risks


class TestPriceAnomalyDetector(unittest.TestCase):
    """Test price anomaly detection logic."""

    def test_detect_price_anomalies_empty_list(self):
        """Test with empty purchase orders list."""
        result = detect_price_anomalies([])
        
        self.assertEqual(result["anomalies"], [])
        self.assertEqual(result["summary"]["total_items_analyzed"], 0)
        self.assertEqual(result["summary"]["anomaly_count"], 0)
        self.assertGreater(len(result["recommendations"]), 0)

    def test_detect_price_anomalies_no_anomalies(self):
        """Test when all prices are consistent."""
        pos = [
            {"item_code": "ITEM-1", "supplier": "Supplier A", "rate": 100, "qty": 10},
            {"item_code": "ITEM-1", "supplier": "Supplier A", "rate": 100, "qty": 5},
            {"item_code": "ITEM-1", "supplier": "Supplier B", "rate": 105, "qty": 8},
        ]
        
        result = detect_price_anomalies(pos)
        
        self.assertIsInstance(result["anomalies"], list)
        self.assertGreaterEqual(result["summary"]["total_items_analyzed"], 1)

    def test_detect_price_anomalies_with_anomaly(self):
        """Test when one price is much higher (anomaly)."""
        pos = [
            {"item_code": "ITEM-1", "supplier": "Supplier A", "rate": 100, "qty": 10},
            {"item_code": "ITEM-1", "supplier": "Supplier B", "rate": 100, "qty": 5},
            {"item_code": "ITEM-1", "supplier": "Supplier C", "rate": 250, "qty": 3},
        ]
        
        result = detect_price_anomalies(pos)
        
        self.assertIn("anomalies", result)
        self.assertIn("summary", result)

    def test_detect_price_anomalies_multiple_items(self):
        """Test detection across multiple items."""
        pos = [
            {"item_code": "ITEM-1", "supplier": "Supplier A", "rate": 100, "qty": 10},
            {"item_code": "ITEM-1", "supplier": "Supplier B", "rate": 105, "qty": 5},
            {"item_code": "ITEM-2", "supplier": "Supplier A", "rate": 50, "qty": 20},
            {"item_code": "ITEM-2", "supplier": "Supplier C", "rate": 150, "qty": 10},
        ]
        
        result = detect_price_anomalies(pos)
        
        self.assertGreaterEqual(result["summary"]["total_items_analyzed"], 2)

    def test_detect_price_anomalies_missing_fields(self):
        """Test handling of missing price fields."""
        pos = [
            {"item_code": "ITEM-1", "supplier": "Supplier A"},
            {"item_code": "ITEM-1", "supplier": "Supplier B", "rate": 100},
        ]
        
        result = detect_price_anomalies(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("anomalies", result)


class TestDelayedOrdersDetector(unittest.TestCase):
    """Test delayed order detection logic."""

    def test_detect_delayed_orders_empty_list(self):
        """Test with empty purchase orders list."""
        result = detect_delayed_orders([])
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)

    def test_detect_delayed_orders_all_ontime(self):
        """Test when all orders are on time."""
        pos = [
            {"name": "PO-001", "transaction_date": "2024-01-01", "delivery_date": "2024-01-10", "status": "Completed"},
            {"name": "PO-002", "transaction_date": "2024-01-05", "delivery_date": "2024-01-15", "status": "Completed"},
        ]
        
        result = detect_delayed_orders(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)

    def test_detect_delayed_orders_with_delays(self):
        """Test when some orders are delayed."""
        pos = [
            {"name": "PO-001", "transaction_date": "2024-01-01", "delivery_date": "2024-01-05", "status": "Pending"},
            {"name": "PO-002", "transaction_date": "2024-01-01", "delivery_date": "2024-01-10", "status": "Completed"},
        ]
        
        result = detect_delayed_orders(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)

    def test_detect_delayed_orders_missing_dates(self):
        """Test handling of missing date fields."""
        pos = [
            {"name": "PO-001", "status": "Pending"},
            {"name": "PO-002", "transaction_date": "2024-01-01", "delivery_date": "2024-01-10"},
        ]
        
        result = detect_delayed_orders(pos)
        
        self.assertIsInstance(result, dict)


class TestPORiskAnalyzer(unittest.TestCase):
    """Test PO risk analysis logic."""

    def test_analyze_po_risks_empty_list(self):
        """Test with empty purchase orders list."""
        result = analyze_po_risks([])
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)
        self.assertIn("orders", result)

    def test_analyze_po_risks_low_risk(self):
        """Test with low-risk orders."""
        pos = [
            {
                "name": "PO-001",
                "supplier": "Supplier A",
                "grand_total": 5000,
                "status": "Completed",
                "transaction_date": "2024-01-01",
                "delivery_date": "2024-01-10"
            },
        ]
        
        result = analyze_po_risks(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)
        self.assertIn("orders", result)

    def test_analyze_po_risks_high_value(self):
        """Test with high-value orders."""
        pos = [
            {
                "name": "PO-001",
                "supplier": "Supplier A",
                "grand_total": 100000,
                "status": "Draft",
                "transaction_date": "2024-01-01",
                "delivery_date": "2024-02-01"
            },
        ]
        
        result = analyze_po_risks(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("orders", result)

    def test_analyze_po_risks_pending_status(self):
        """Test with pending orders (higher risk)."""
        pos = [
            {
                "name": "PO-001",
                "supplier": "Supplier A",
                "grand_total": 5000,
                "status": "Pending",
                "transaction_date": "2024-01-01",
                "delivery_date": "2024-01-10"
            },
        ]
        
        result = analyze_po_risks(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("orders", result)

    def test_analyze_po_risks_missing_fields(self):
        """Test handling of missing fields."""
        pos = [
            {"name": "PO-001"},
            {"name": "PO-002", "supplier": "Supplier A", "grand_total": 5000},
        ]
        
        result = analyze_po_risks(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("orders", result)

    def test_analyze_po_risks_multiple_orders(self):
        """Test analyzing multiple orders."""
        pos = [
            {
                "name": "PO-001",
                "supplier": "Supplier A",
                "grand_total": 5000,
                "status": "Completed",
                "transaction_date": "2024-01-01",
                "delivery_date": "2024-01-10"
            },
            {
                "name": "PO-002",
                "supplier": "Supplier B",
                "grand_total": 50000,
                "status": "Pending",
                "transaction_date": "2024-01-05",
                "delivery_date": "2024-02-05"
            },
            {
                "name": "PO-003",
                "supplier": "Supplier A",
                "grand_total": 3000,
                "status": "Submitted",
                "transaction_date": "2024-01-10",
                "delivery_date": "2024-01-20"
            },
        ]
        
        result = analyze_po_risks(pos)
        
        self.assertIsInstance(result, dict)
        self.assertIn("orders", result)


if __name__ == "__main__":
    unittest.main()
