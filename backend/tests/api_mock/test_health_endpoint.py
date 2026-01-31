"""
Tests for HEALTH endpoint (1 endpoint).
Tests: GET /health
"""

import unittest
from backend.tests.api_mock.base_test import APITestBase


class TestHealthEndpoint(APITestBase):
    """Tests for GET /health endpoint."""
    
    def test_health_endpoint_returns_ok(self):
        """GET /health returns 200 with status ok."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'ok')
    
    def test_health_endpoint_returns_json(self):
        """Health endpoint returns valid JSON."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())
    
    def test_health_endpoint_contains_status(self):
        """Health response contains status field."""
        response = self.client.get("/health")
        
        data = response.json()
        self.assertIn('status', data)


if __name__ == "__main__":
    unittest.main()
