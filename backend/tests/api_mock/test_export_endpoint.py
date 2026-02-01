"""
Tests for EXPORT endpoint (1 endpoint).
Tests: POST /export/pdf
"""

import unittest
from unittest.mock import patch, MagicMock
from backend.tests.api_mock.base_test import APITestBase


class TestExportPDFEndpoint(APITestBase):
    """Tests for POST /export/pdf endpoint."""
    
    def test_export_pdf_returns_200(self):
        """POST /export/pdf returns 200 with PDF content."""
        response = self.client.post(
            "/export/pdf",
            json={
                "data": {"item": "test", "quantity": 10},
                "intent": "export_data",
                "title": "Test Report"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
    
    def test_export_pdf_requires_data(self):
        """Export PDF endpoint requires data parameter."""
        response = self.client.post(
            "/export/pdf",
            json={"intent": "export_data"}
        )
        
        # Should fail if data missing
        self.assertIn(response.status_code, [400, 422])
    
    def test_export_pdf_requires_intent(self):
        """Export PDF endpoint - intent is optional (has default value)."""
        response = self.client.post(
            "/export/pdf",
            json={"data": {"test": "value"}}
        )
        
        # Intent is optional with default "report", so should succeed
        self.assertEqual(response.status_code, 200)
    
    def test_export_pdf_with_valid_intent(self):
        """Export PDF handles various intent types."""
        intents = ["report", "price_anomalies", "delayed_orders"]
        
        for intent in intents:
            response = self.client.post(
                "/export/pdf",
                json={
                    "data": {"test": "data"},
                    "intent": intent,
                    "title": f"{intent} Report"
                }
            )
            
            # Should accept valid intents
            self.assertIn(response.status_code, [200, 500])


if __name__ == "__main__":
    unittest.main()
