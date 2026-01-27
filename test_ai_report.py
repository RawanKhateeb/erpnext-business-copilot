"""
Unit tests for AI Report Generator and /ai/report endpoint.

Tests cover:
- AI report generation with mocked OpenAI
- Error handling (API failures, rate limits, etc.)
- PO summary computation
- Frontend integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.ai_report_generator import AIReportGenerator
from app.main import _compute_po_summary
from fastapi.testclient import TestClient
from app.main import app


class TestAIReportGenerator:
    """Test AI Report Generator module."""
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('app.ai_report_generator.OpenAI')
    def test_generate_report_success(self, mock_openai_class):
        """Test successful report generation."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a procurement report..."
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create generator and generate report
        generator = AIReportGenerator()
        summary = {
            'total_spend': 50000,
            'po_count': 25,
            'pending_count': 5,
            'status_breakdown': {'Draft': 5, 'Submitted': 20},
            'top_suppliers': [('Acme Corp', 25000), ('Smith Ltd', 15000)],
            'date_range': 'January 2026'
        }
        
        result = generator.generate_procurement_report(summary)
        
        assert result['success'] is True
        assert 'procurement report' in result['report'].lower()
        assert result['summary'] == summary
        assert 'generated_at' in result
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('app.ai_report_generator.OpenAI')
    def test_rate_limit_error(self, mock_openai_class):
        """Test handling of rate limit errors."""
        try:
            from openai import RateLimitError
        except ImportError:
            # Legacy API
            from openai.error import RateLimitError
        
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded", None, None)
        
        generator = AIReportGenerator()
        summary = {'total_spend': 50000}
        
        result = generator.generate_procurement_report(summary)
        
        assert result['success'] is False
        assert 'rate limit' in result.get('message', '').lower() or result.get('error') == 'rate_limit'
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-test-key'})
    @patch('app.ai_report_generator.OpenAI')
    def test_api_connection_error(self, mock_openai_class):
        """Test handling of connection errors."""
        try:
            from openai import APIConnectionError
        except ImportError:
            # Legacy API
            from openai.error import APIConnectionError
        
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = APIConnectionError("Connection failed")
        
        generator = AIReportGenerator()
        summary = {'total_spend': 50000}
        
        result = generator.generate_procurement_report(summary)
        
        assert result['success'] is False
        assert 'connection' in result.get('message', '').lower() or result.get('error') == 'connection_error'
    
    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                AIReportGenerator()


class TestPoSummaryComputation:
    """Test PO summary statistics computation."""
    
    def test_empty_po_list(self):
        """Test with empty purchase orders list."""
        summary = _compute_po_summary([])
        
        assert summary['total_spend'] == 0
        assert summary['po_count'] == 0
        assert summary['pending_count'] == 0
        assert summary['status_breakdown'] == {}
        assert summary['top_suppliers'] == []
    
    def test_single_po(self):
        """Test with single purchase order."""
        pos = [{
            'grand_total': 1000,
            'status': 'Submitted',
            'supplier': 'Acme Corp'
        }]
        
        summary = _compute_po_summary(pos)
        
        assert summary['total_spend'] == 1000
        assert summary['po_count'] == 1
        assert summary['pending_count'] == 0
        assert summary['status_breakdown']['Submitted'] == 1
        assert ('Acme Corp', 1000) in summary['top_suppliers']
    
    def test_multiple_pos_with_pending(self):
        """Test with multiple POs including pending ones."""
        pos = [
            {'grand_total': 1000, 'status': 'Submitted', 'supplier': 'Acme'},
            {'grand_total': 2000, 'status': 'Pending', 'supplier': 'Smith'},
            {'grand_total': 1500, 'status': 'Draft', 'supplier': 'Acme'},
        ]
        
        summary = _compute_po_summary(pos)
        
        assert summary['total_spend'] == 4500
        assert summary['po_count'] == 3
        assert summary['pending_count'] == 2  # Pending + Draft
        assert summary['status_breakdown']['Submitted'] == 1
        assert summary['status_breakdown']['Pending'] == 1
        assert summary['status_breakdown']['Draft'] == 1
    
    def test_top_suppliers_sorted(self):
        """Test that top suppliers are sorted by spend."""
        pos = [
            {'grand_total': 500, 'status': 'Submitted', 'supplier': 'C Corp'},
            {'grand_total': 2000, 'status': 'Submitted', 'supplier': 'A Corp'},
            {'grand_total': 1000, 'status': 'Submitted', 'supplier': 'B Corp'},
        ]
        
        summary = _compute_po_summary(pos)
        
        assert summary['top_suppliers'][0] == ('A Corp', 2000)
        assert summary['top_suppliers'][1] == ('B Corp', 1000)
        assert summary['top_suppliers'][2] == ('C Corp', 500)


class TestAIReportEndpoint:
    """Test /ai/report endpoint."""
    
    @patch('app.main.AIReportGenerator')
    @patch('app.main.get_client')
    def test_ai_report_success(self, mock_get_client, mock_ai_gen_class):
        """Test successful AI report endpoint."""
        # Mock ERPNext client
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {'grand_total': 5000, 'status': 'Submitted', 'supplier': 'Test Supplier'},
        ]
        mock_get_client.return_value = mock_client
        
        # Mock AI generator
        mock_ai_gen = MagicMock()
        mock_ai_gen_class.return_value = mock_ai_gen
        mock_ai_gen.generate_procurement_report.return_value = {
            'success': True,
            'report': 'Test report',
            'summary': {'total_spend': 5000},
            'generated_at': '2026-01-27T00:00:00'
        }
        
        client = TestClient(app)
        response = client.post('/ai/report', json={'query': 'Generate report'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['intent'] == 'ai_report'
        assert data['ai_generated'] is True
        assert 'report' in data['answer']
    
    @patch('app.main.get_client')
    def test_ai_report_no_po_data(self, mock_get_client):
        """Test when no purchase order data is available."""
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = []
        mock_get_client.return_value = mock_client
        
        client = TestClient(app)
        response = client.post('/ai/report', json={'query': 'Generate report'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert 'No purchase order' in data['message']
    
    @patch('app.main.AIReportGenerator')
    @patch('app.main.get_client')
    def test_ai_report_openai_error(self, mock_get_client, mock_ai_gen_class):
        """Test when OpenAI API fails."""
        # Mock ERPNext client
        mock_client = MagicMock()
        mock_client.list_purchase_orders.return_value = [
            {'grand_total': 5000, 'status': 'Submitted', 'supplier': 'Test Supplier'},
        ]
        mock_get_client.return_value = mock_client
        
        # Mock AI generator returning error
        mock_ai_gen = MagicMock()
        mock_ai_gen_class.return_value = mock_ai_gen
        mock_ai_gen.generate_procurement_report.return_value = {
            'success': False,
            'message': 'AI service unavailable',
            'error': 'api_error'
        }
        
        client = TestClient(app)
        response = client.post('/ai/report', json={'query': 'Generate report'})
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert data['ai_generated'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
