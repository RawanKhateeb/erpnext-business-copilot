"""
Unittest-based API tests for AI report endpoint.
Tests POST /ai/report using FastAPI TestClient and unittest.mock.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class TestAIReportEndpoint(unittest.TestCase):
    """Test AI report endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    # ============ POST /ai/report ============
    @patch('app.controllers.ai.get_client')
    @patch('app.controllers.ai.AIReportGenerator')
    def test_ai_report_success(self, mock_report_gen, mock_get_client):
        """Test POST /ai/report generates report successfully."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000, "status": "Submitted"}
        ]
        mock_get_client.return_value = mock_client

        mock_generator = MagicMock()
        mock_generator.generate.return_value = "Monthly procurement report shows stable performance."
        mock_report_gen.return_value = mock_generator

        response = self.client.post(
            "/ai/report",
            json={"query": "Generate monthly report"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("intent"), "ai_report")
        self.assertTrue(data.get("ai_generated"))
        self.assertIn("answer", data)

    @patch('app.controllers.ai.get_client')
    def test_ai_report_no_purchase_orders(self, mock_get_client):
        """Test POST /ai/report when no purchase orders available."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = []
        mock_get_client.return_value = mock_client

        response = self.client.post(
            "/ai/report",
            json={"query": "Generate report"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))
        self.assertIn("No purchase order", data.get("message", ""))

    @patch('app.controllers.ai.get_client')
    def test_ai_report_erp_connection_error(self, mock_get_client):
        """Test POST /ai/report handles ERP connection errors."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.side_effect = Exception("Connection failed")
        mock_get_client.return_value = mock_client

        response = self.client.post(
            "/ai/report",
            json={"query": "Generate report"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get("success"))

    @patch('app.controllers.ai.get_client')
    @patch('app.controllers.ai.AIReportGenerator')
    def test_ai_report_with_summary(self, mock_report_gen, mock_get_client):
        """Test POST /ai/report response includes summary data."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000, "status": "Submitted"},
            {"name": "PO-002", "supplier": "Supplier B", "grand_total": 3000, "status": "Draft"}
        ]
        mock_get_client.return_value = mock_client

        mock_generator = MagicMock()
        mock_generator.generate.return_value = "Analysis complete."
        mock_report_gen.return_value = mock_generator

        response = self.client.post(
            "/ai/report",
            json={"query": "Generate comprehensive report"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        # Response should include answer or summary with po information
        self.assertIn("answer", data)

    @patch('app.controllers.ai.get_client')
    @patch('app.controllers.ai.AIReportGenerator')
    def test_ai_report_response_structure(self, mock_report_gen, mock_get_client):
        """Test POST /ai/report response has required structure."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000, "status": "Submitted"}
        ]
        mock_get_client.return_value = mock_client

        mock_generator = MagicMock()
        mock_generator.generate.return_value = "Report generated."
        mock_report_gen.return_value = mock_generator

        response = self.client.post(
            "/ai/report",
            json={"query": "Generate report", "period": "month"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check required fields
        self.assertIn("success", data)
        self.assertIn("intent", data)
        self.assertIn("ai_generated", data)

    @patch('app.controllers.ai.get_client')
    def test_ai_report_missing_query(self, mock_get_client):
        """Test POST /ai/report with missing query parameter."""
        response = self.client.post(
            "/ai/report",
            json={}
        )

        # Should return 422 (Unprocessable Entity) for missing required field
        self.assertEqual(response.status_code, 422)

    @patch('app.controllers.ai.get_client')
    @patch('app.controllers.ai.AIReportGenerator')
    def test_ai_report_procurement_analysis(self, mock_report_gen, mock_get_client):
        """Test POST /ai/report with procurement analysis query."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {"name": "PO-001", "supplier": "Supplier A", "grand_total": 5000, "status": "Completed"},
            {"name": "PO-002", "supplier": "Supplier A", "grand_total": 3500, "status": "Submitted"},
            {"name": "PO-003", "supplier": "Supplier B", "grand_total": 2000, "status": "Draft"}
        ]
        mock_get_client.return_value = mock_client

        mock_generator = MagicMock()
        mock_generator.generate.return_value = "Procurement analysis shows Supplier A is our top vendor."
        mock_report_gen.return_value = mock_generator

        response = self.client.post(
            "/ai/report",
            json={"query": "Analyze procurement trends"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("intent"), "ai_report")


if __name__ == "__main__":
    unittest.main()
