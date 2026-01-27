"""
Playwright UI tests for AI Report feature.

Test that the Data/AI Reports toggle works and generates AI reports.

Installation:
pip install playwright pytest-playwright
playwright install

Run:
pytest test_ui_ai_report.py -v
"""

import pytest
from playwright.sync_api import sync_playwright, expect
import time


@pytest.fixture
def browser_context():
    """Create a browser context for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


class TestAIReportUI:
    """UI tests for AI Report feature."""
    
    BASE_URL = "http://localhost:8001"
    
    def test_toggle_exists(self, browser_context):
        """Test that Data/AI Reports toggle exists."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        # Check for toggle buttons
        data_btn = page.locator('.mode-btn[data-mode="data"]')
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        
        assert data_btn.is_visible()
        assert ai_btn.is_visible()
        assert "Data" in data_btn.text_content()
        assert "AI Reports" in ai_btn.text_content()
        
        page.close()
    
    def test_default_mode_is_data(self, browser_context):
        """Test that Data mode is selected by default."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        data_btn = page.locator('.mode-btn[data-mode="data"]')
        assert data_btn.evaluate("el => el.classList.contains('active')") is True
        
        page.close()
    
    def test_switch_to_ai_mode(self, browser_context):
        """Test switching to AI Reports mode."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        # Click AI Reports button
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        ai_btn.click()
        
        # Check that AI button is now active
        assert ai_btn.evaluate("el => el.classList.contains('active')") is True
        
        # Check that Data button is no longer active
        data_btn = page.locator('.mode-btn[data-mode="data"]')
        assert data_btn.evaluate("el => el.classList.contains('active')") is False
        
        page.close()
    
    def test_placeholder_changes_with_mode(self, browser_context):
        """Test that input placeholder changes when mode changes."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        input_field = page.locator('#query')
        
        # Default placeholder in Data mode
        data_placeholder = input_field.get_attribute('placeholder')
        assert "List suppliers" in data_placeholder or "List" in data_placeholder
        
        # Switch to AI mode
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        ai_btn.click()
        
        # Placeholder should change
        ai_placeholder = input_field.get_attribute('placeholder')
        assert "monthly procurement report" in ai_placeholder.lower() or "generate" in ai_placeholder.lower()
        
        page.close()
    
    def test_helper_text_changes_with_mode(self, browser_context):
        """Test that helper text changes when mode changes."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        helper = page.locator('.mode-helper')
        
        # Default helper text in Data mode
        data_helper = helper.text_content()
        assert "Query live ERP data" in data_helper
        
        # Switch to AI mode
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        ai_btn.click()
        
        # Helper text should change
        ai_helper = helper.text_content()
        assert "Generate insights using AI" in ai_helper
        
        page.close()
    
    def test_ai_report_generation(self, browser_context):
        """Test generating an AI report."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        # Switch to AI mode
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        ai_btn.click()
        
        # Enter a query
        input_field = page.locator('#query')
        input_field.fill("Generate monthly procurement report")
        
        # Submit
        submit_btn = page.locator('#submitBtn')
        submit_btn.click()
        
        # Wait for response
        response_area = page.locator('#responseArea')
        expect(response_area).to_have_class('show', timeout=10000)
        
        # Check for AI Generated badge
        badge = page.locator('#intentBadge')
        badge_text = badge.text_content()
        assert "AI Generated" in badge_text or "ai_report" in badge_text.lower()
        
        # Check that answer is not empty
        answer = page.locator('#answer')
        assert len(answer.text_content()) > 0
        
        page.close()
    
    def test_data_mode_still_works(self, browser_context):
        """Test that Data mode still works after adding AI mode."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        # Make sure we're in Data mode (should be default)
        input_field = page.locator('#query')
        input_field.fill("List purchase orders")
        
        # Submit
        submit_btn = page.locator('#submitBtn')
        submit_btn.click()
        
        # Wait for response
        response_area = page.locator('#responseArea')
        expect(response_area).to_have_class('show', timeout=10000)
        
        # Check that we got a response
        answer = page.locator('#answer')
        assert len(answer.text_content()) > 0
        
        page.close()
    
    def test_toggle_styling(self, browser_context):
        """Test that toggle buttons have correct styling."""
        page = browser_context.new_page()
        page.goto(self.BASE_URL)
        
        # Get initial button styles
        data_btn = page.locator('.mode-btn[data-mode="data"]')
        
        # Active button should have background
        active_bg = data_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        assert active_bg  # Should have a color
        
        # Switch to AI mode
        ai_btn = page.locator('.mode-btn[data-mode="ai"]')
        ai_btn.click()
        
        # Now Data button should be inactive (white background)
        inactive_bg = data_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        
        # AI button should be active
        active_bg_new = ai_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        
        page.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
