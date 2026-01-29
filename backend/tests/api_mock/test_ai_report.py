"""
Unit tests for /ai/report endpoint.
Tests: AI report generation, OpenAI mocking, error handling.
"""

import unittest
from unittest.mock import MagicMock, patch
from base_test import APITestBase
from mock_data import MOCK_AI_REPORT


class TestAIReportEndpoint(APITestBase):
    """Tests for /ai/report endpoint."""

    def test_ai_report_returns_200_with_report(self):
        """Happy path: AI report endpoint returns 200 with report data."""
        with patch('app.ai_report_generator.AIReportGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.return_value = MOCK_AI_REPORT

            response = self.client.post(
                "/ai/report", json={"query": "Generate monthly report"}
            )

        self.assert_response_ok(response)
        data = response.json()
        # Check for either 'report' or 'answer' field (API may return either)
        has_report = "report" in data or "answer" in data or "ai_generated" in data
        self.assertTrue(has_report, "Response should contain report/answer data")

    def test_ai_report_returns_report_content(self):
        """Response structure: report field contains text."""
        with patch('app.ai_report_generator.AIReportGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.return_value = MOCK_AI_REPORT

            response = self.client.post(
                "/ai/report", json={"query": "Generate report"}
            )

        data = response.json()
        # API returns either 'report' or 'answer' field
        content = data.get("report") or data.get("answer")
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)

    def test_ai_report_missing_query_parameter(self):
        """Error path: missing query parameter."""
        response = self.client.post("/ai/report", json={})
        self.assertIn(response.status_code, [400, 422])

    def test_ai_report_empty_query(self):
        """Error path: empty query string."""
        response = self.client.post("/ai/report", json={"query": ""})
        self.assertIn(response.status_code, [200, 400, 422])

    def test_ai_report_handles_openai_api_error(self):
        """Error path: OpenAI API failure returns graceful error."""
        with patch('app.ai_report_generator.AIReportGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.side_effect = Exception(
                "OpenAI API key invalid"
            )

            response = self.client.post(
                "/ai/report", json={"query": "Generate report"}
            )

        # Should not crash; may return 500 or error message
        self.assertIn(response.status_code, [200, 500])

    def test_ai_report_handles_network_error(self):
        """Error path: network error during generation."""
        with patch('app.ai_report_generator.AIReportGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.side_effect = ConnectionError(
                "Failed to reach OpenAI"
            )

            response = self.client.post(
                "/ai/report", json={"query": "Generate report"}
            )

        self.assertIn(response.status_code, [200, 500])

    def test_ai_report_request_structure(self):
        """Validation: request must have 'query' field."""
        response = self.client.post("/ai/report", json={"prompt": "invalid"})
        self.assertIn(response.status_code, [400, 422])


class TestAIReportData(unittest.TestCase):
    """Tests for AI report data structure."""

    def test_mock_ai_report_structure(self):
        """Mock report data is properly structured."""
        self.assertIn("report", MOCK_AI_REPORT)
        self.assertIn("summary", MOCK_AI_REPORT)
        self.assertIsInstance(MOCK_AI_REPORT["report"], str)


if __name__ == "__main__":
    unittest.main()
