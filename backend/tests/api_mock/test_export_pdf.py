"""
Unittest-based API tests for export endpoint.
Tests POST /export/pdf using FastAPI TestClient and unittest.mock.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class TestExportPDFEndpoint(unittest.TestCase):
    """Test export PDF endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    # ============ POST /export/pdf ============
    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_success(self, mock_generate_pdf):
        """Test POST /export/pdf generates PDF successfully."""
        mock_pdf_bytes = b"PDF content here"
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {
                    "items": [
                        {"name": "PO-001", "value": 5000},
                        {"name": "PO-002", "value": 3000}
                    ]
                },
                "intent": "list_purchase_orders",
                "title": "Purchase Orders Report"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("attachment", response.headers.get("content-disposition", ""))
        self.assertEqual(response.content, mock_pdf_bytes)

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_with_default_intent(self, mock_generate_pdf):
        """Test POST /export/pdf with default intent."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"sample": "data"}
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        # Verify generate_pdf_report was called with default intent="report"
        call_args = mock_generate_pdf.call_args
        self.assertEqual(call_args.kwargs["intent"], "report")

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_with_anomalies_intent(self, mock_generate_pdf):
        """Test POST /export/pdf with price_anomalies intent."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {
                    "anomalies": [
                        {"item": "ITEM-1", "variance": "25%"}
                    ]
                },
                "intent": "detect_price_anomalies",
                "title": "Price Anomalies Report"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        # Verify intent was passed correctly
        call_args = mock_generate_pdf.call_args
        self.assertEqual(call_args.kwargs["intent"], "detect_price_anomalies")

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_response_has_filename(self, mock_generate_pdf):
        """Test POST /export/pdf response includes filename."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"items": []},
                "intent": "list_purchase_orders"
            }
        )

        self.assertEqual(response.status_code, 200)
        disposition = response.headers.get("content-disposition", "")
        self.assertIn("attachment", disposition)
        self.assertIn("filename", disposition)
        self.assertIn("list_purchase_orders", disposition)

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_with_custom_title(self, mock_generate_pdf):
        """Test POST /export/pdf with custom title."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        custom_title = "Custom Procurement Report"
        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"items": []},
                "title": custom_title
            }
        )

        self.assertEqual(response.status_code, 200)
        # Verify title was passed to generator
        call_args = mock_generate_pdf.call_args
        self.assertEqual(call_args.kwargs["title"], custom_title)

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_generation_error(self, mock_generate_pdf):
        """Test POST /export/pdf handles generation errors."""
        mock_generate_pdf.side_effect = Exception("PDF generation failed")

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"items": []},
                "intent": "report"
            }
        )

        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("PDF generation failed", data["detail"])

    def test_export_pdf_missing_data(self):
        """Test POST /export/pdf with missing data field."""
        response = self.client.post(
            "/export/pdf",
            json={
                "intent": "report"
            }
        )

        # Should return 422 (Unprocessable Entity) for missing required field
        self.assertEqual(response.status_code, 422)

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_with_complex_data(self, mock_generate_pdf):
        """Test POST /export/pdf with complex nested data structure."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        complex_data = {
            "summary": {
                "total": 15000,
                "count": 3,
                "average": 5000
            },
            "items": [
                {
                    "name": "PO-001",
                    "supplier": "Supplier A",
                    "details": {
                        "grand_total": 5000,
                        "items_count": 5
                    }
                }
            ],
            "metadata": {
                "generated_at": "2024-02-03",
                "period": "February 2024"
            }
        }

        response = self.client.post(
            "/export/pdf",
            json={
                "data": complex_data,
                "intent": "ai_report",
                "title": "Comprehensive Procurement Report"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        # Verify data was passed correctly
        call_args = mock_generate_pdf.call_args
        self.assertEqual(call_args.kwargs["data"], complex_data)

    @patch('app.controllers.export.generate_pdf_report')
    def test_export_pdf_filename_format(self, mock_generate_pdf):
        """Test POST /export/pdf filename is correctly formatted."""
        mock_pdf_bytes = b"PDF content"
        mock_generate_pdf.return_value = mock_pdf_bytes

        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"items": []},
                "intent": "detect_delayed_orders"
            }
        )

        self.assertEqual(response.status_code, 200)
        disposition = response.headers.get("content-disposition", "")
        # Filename should follow pattern: copilot_report_{intent}.pdf
        self.assertIn("copilot_report_detect_delayed_orders.pdf", disposition)


if __name__ == "__main__":
    unittest.main()
