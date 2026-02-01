"""
Base test class for API tests using unittest and FastAPI TestClient.
Provides common setup and mock utilities.
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.main import app


class APITestBase(unittest.TestCase):
    """Base class for all API tests."""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)

    def setUp(self):
        """Set up before each test."""
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up after each test."""
        pass

    def assert_response_ok(self, response, expected_status=200):
        """Assert that response is successful."""
        self.assertEqual(response.status_code, expected_status)

    def assert_json_keys(self, response_data, expected_keys):
        """Assert that response contains all expected keys."""
        for key in expected_keys:
            self.assertIn(key, response_data, f"Missing key: {key}")

    def mock_erpnext_client(self, return_value=None):
        """Mock ERPNextClient to avoid real API calls."""
        patcher = patch('app.main.get_client')
        mock_client = patcher.start()
        if return_value:
            mock_client.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock_client.return_value
