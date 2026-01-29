"""
AI Report Generator

Generates procurement reports using OpenAI based on ERPNext data.
Uses OpenAI to create narrative summaries of purchasing data.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

# Try to import from modern openai package (>=1.0)
try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    # Fallback to legacy openai API (<1.0)
    import openai
    from openai.error import APIError, RateLimitError, APIConnectionError
    OpenAI = None

logger = logging.getLogger(__name__)


class AIReportGenerator:
    """Generates AI-powered procurement reports using OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client from environment variable."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Use modern API if available
        if OpenAI is not None:
            self.client = OpenAI(api_key=api_key)
            self.use_modern_api = True
        else:
            # Fall back to legacy API
            import openai
            openai.api_key = api_key
            self.client = openai
            self.use_modern_api = False
    
    def generate_procurement_report(self, summary: Dict[str, Any], query: str = None) -> Dict[str, Any]:
        """
        Generate a structured procurement report from summary data.
        
        Args:
            summary: Dictionary containing:
                - total_spend: Total spending amount
                - po_count: Number of purchase orders
                - pending_count: Number of pending orders
                - status_breakdown: Dict of statuses and counts
                - top_suppliers: List of (supplier_name, amount) tuples
                - date_range: str describing the period
            
            query: Optional user query for context
        
        Returns:
            {
                'success': bool,
                'report': str (narrative report),
                'sections': dict with structured report sections,
                'metrics': dict with key metrics,
                'summary': dict,
                'generated_at': str (ISO timestamp)
            }
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(summary, query)
            
            # Call OpenAI based on API version
            if self.use_modern_api:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a procurement analyst. Generate professional, concise procurement reports based on supplied data. Use business language and highlight key insights."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=30
                )
                report_text = response.choices[0].message.content
            else:
                # Legacy API
                response = self.client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a procurement analyst. Generate professional, concise procurement reports based on supplied data. Use business language and highlight key insights."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=30
                )
                report_text = response.choices[0].message['content']
            
            # Extract structured sections from the report
            sections = self._parse_report_sections(report_text)
            
            # Prepare metrics for display
            metrics = self._prepare_metrics(summary)
            
            return {
                'success': True,
                'report': report_text,
                'sections': sections,
                'metrics': metrics,
                'summary': summary,
                'generated_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            error_str = str(e).lower()
            
            if 'rate limit' in error_str:
                logger.error(f"OpenAI rate limit exceeded: {str(e)}")
                return {
                    'success': False,
                    'message': 'AI service is temporarily overloaded. Please try again shortly.',
                    'error': 'rate_limit'
                }
            elif 'connection' in error_str or 'timeout' in error_str:
                logger.error(f"OpenAI API connection error: {str(e)}")
                return {
                    'success': False,
                    'message': 'Unable to connect to AI service. Please check your internet connection.',
                    'error': 'connection_error'
                }
            else:
                logger.error(f"OpenAI API error: {str(e)}")
                return {
                    'success': False,
                    'message': 'AI service encountered an error. Please try again.',
                    'error': 'api_error'
                }
    
    @staticmethod
    def _build_prompt(summary: Dict[str, Any], query: str = None) -> str:
        """
        Build the prompt for OpenAI.
        
        Args:
            summary: Procurement data summary
            query: Optional user query
        
        Returns:
            Formatted prompt string
        """
        date_range = summary.get('date_range', 'This Period')
        total_spend = float(summary.get('total_spend', 0) or 0)
        po_count = int(summary.get('po_count', 0) or 0)
        pending_count = int(summary.get('pending_count', 0) or 0)
        status_breakdown = summary.get('status_breakdown', {})
        top_suppliers = summary.get('top_suppliers', [])
        
        # Format top suppliers
        suppliers_text = ""
        if top_suppliers:
            suppliers_text = "\n\nTop Suppliers by Spend:"
            for i, supplier_info in enumerate(top_suppliers[:5], 1):
                if isinstance(supplier_info, (tuple, list)):
                    name, amount = supplier_info[0], float(supplier_info[1] or 0)
                else:
                    name = str(supplier_info.get('name', 'Unknown'))
                    amount = float(supplier_info.get('amount', 0) or 0)
                suppliers_text += f"\n{i}. {name}: ${amount:,.2f}"
        
        # Format status breakdown
        status_text = ""
        if status_breakdown:
            status_text = "\n\nOrder Status Distribution:"
            for status, count in status_breakdown.items():
                status_text += f"\n- {status}: {int(count or 0)}"
        
        prompt = f"""Generate a CONCISE procurement report for {date_range}.

PROCUREMENT DATA:
- Total Spending: ${total_spend:,.2f}
- Total Purchase Orders: {po_count}
- Pending Orders: {pending_count}
{status_text}{suppliers_text}

CRITICAL FORMAT REQUIREMENT:
Format the report as bullet points separated by " | " (pipe character).
Use NO paragraphs, NO line breaks, NO markdown formatting.
Each bullet should be SHORT (5-10 words max).
Put all content on one continuous line with bullets separated by " | ".

Example format: Bullet 1 | Bullet 2 | Bullet 3 | Bullet 4 | Bullet 5 | etc.

Generate bullet points covering:
- Executive summary (overview of procurement)
- Total spending and order count
- Top suppliers and amounts
- Order status distribution  
- Key metrics and performance indicators
- One actionable recommendation
- Risk assessment if applicable

Keep it SHORT, SCANNABLE, and ALL ON ONE LINE with pipe separators."""
        
        if query:
            prompt += f"\n\nUser context: {query}"
        
        return prompt

    @staticmethod
    def _parse_report_sections(report_text: str) -> Dict[str, str]:
        """
        Parse the report into logical sections.
        
        Args:
            report_text: Full report narrative
        
        Returns:
            Dictionary with parsed sections
        """
        sections = {
            'overview': '',
            'analysis': '',
            'trends': '',
            'recommendation': ''
        }
        
        paragraphs = report_text.split('\n\n')
        
        if len(paragraphs) >= 1:
            sections['overview'] = paragraphs[0]
        if len(paragraphs) >= 2:
            sections['analysis'] = paragraphs[1]
        if len(paragraphs) >= 3:
            sections['trends'] = paragraphs[2]
        if len(paragraphs) >= 4:
            sections['recommendation'] = paragraphs[3]
        
        return sections

    @staticmethod
    def _prepare_metrics(summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare key metrics for display.
        
        Args:
            summary: Procurement data summary
        
        Returns:
            Dictionary with formatted metrics
        """
        total_spend = summary.get('total_spend', 0)
        po_count = summary.get('po_count', 0)
        pending_count = summary.get('pending_count', 0)
        status_breakdown = summary.get('status_breakdown', {})
        top_suppliers = summary.get('top_suppliers', [])
        
        # Calculate average spend per PO
        avg_spend_per_po = total_spend / po_count if po_count > 0 else 0
        
        # Calculate pending percentage
        pending_percentage = (pending_count / po_count * 100) if po_count > 0 else 0
        
        # Get top supplier
        top_supplier_name = top_suppliers[0][0] if top_suppliers else 'N/A'
        top_supplier_spend = top_suppliers[0][1] if top_suppliers else 0
        
        return {
            'total_spend': total_spend,
            'po_count': po_count,
            'pending_count': pending_count,
            'pending_percentage': round(pending_percentage, 1),
            'avg_spend_per_po': avg_spend_per_po,
            'top_supplier': top_supplier_name,
            'top_supplier_spend': top_supplier_spend,
            'supplier_count': len(top_suppliers),
            'status_breakdown': status_breakdown,
            'top_suppliers': top_suppliers
        }
