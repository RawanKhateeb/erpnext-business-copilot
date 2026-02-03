"""
Unittest-based API tests for health endpoint.
Tests GET /health using FastAPI TestClient and unittest.
"""

import unittest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class TestHealthEndpoint(unittest.TestCase):
    """Test health check endpoint."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    # ============ GET /health ============
    def test_health_endpoint_returns_ok(self):
        """Test GET /health returns 200 status."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

    def test_health_endpoint_returns_json(self):
        """Test GET /health returns JSON response."""
        response = self.client.get("/health")

        self.assertEqual(response.headers["content-type"], "application/json")
        data = response.json()
        self.assertIsInstance(data, dict)

    def test_health_endpoint_contains_status(self):
        """Test GET /health response contains status field."""
        response = self.client.get("/health")

        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

    def test_health_endpoint_no_query_params(self):
        """Test GET /health ignores query parameters."""
        response = self.client.get("/health?foo=bar&baz=qux")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_health_endpoint_multiple_calls(self):
        """Test GET /health can be called multiple times."""
        for _ in range(3):
            response = self.client.get("/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ok")


if __name__ == "__main__":
    unittest.main()
