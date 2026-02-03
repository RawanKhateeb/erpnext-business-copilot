"""UI Tests: E2E and Feature tests for Copilot."""
import os
from playwright.sync_api import Page


# Selectors
QUERY_INPUT = '[data-testid="query-input"]'
ASK_BUTTON = '[data-testid="ask-button"]'
MODE_DATA = '[data-testid="mode-data"]'
MODE_COPILOT = '[data-testid="mode-copilot"]'
RESULTS_TABLE = '[data-testid="results-table"]'
EXPORT_BUTTON = '[data-testid="export-button"]'
ERROR_BANNER = '[data-testid="error-banner"]'
RESULTS_CONTAINER = '[data-testid="results-container"]'


def get_base_url():
    """Get base URL from environment or use default."""
    return os.getenv("BASE_URL", "https://wiser-rosina-vaulted.ngrok-free.dev")


def test_e2e_data_mode_ask_question(page: Page):
    """
    E2E Test: Complete user flow in Data mode.
    
    Steps:
    1. Navigate to homepage
    2. Select Data mode
    3. Enter query "Show suppliers"
    4. Click Ask button
    5. Assert results appear
    6. Assert no error
    """
    base_url = get_base_url()
    
    # Step 1: Navigate to homepage
    page.goto(base_url, wait_until="load")
    
    # Step 2: Select Data mode
    page.click(MODE_DATA)
    page.wait_for_load_state("networkidle")
    
    # Step 3: Enter query
    page.fill(QUERY_INPUT, "Show suppliers")
    
    # Step 4: Click Ask
    page.click(ASK_BUTTON)
    
    # Step 5: Wait for results
    page.wait_for_selector(
        f"{RESULTS_TABLE}, {RESULTS_CONTAINER}",
        timeout=10000,
        state="visible"
    )
    
    # Assert results are visible
    has_results = page.is_visible(RESULTS_TABLE) or page.is_visible(RESULTS_CONTAINER)
    assert has_results, "Results should be displayed"
    
    # Step 6: Assert no error
    has_error = page.is_visible(ERROR_BANNER)
    assert not has_error, "No error should be shown"


def test_export_button_appears_after_results(page: Page):
    """
    Feature Test: Export button appears after getting results.
    
    Steps:
    1. Navigate to homepage
    2. Select Copilot mode
    3. Ask a question to get results
    4. Assert export button is visible
    """
    base_url = get_base_url()
    
    # Step 1: Navigate to homepage
    page.goto(base_url, wait_until="load")
    
    # Step 2: Select Copilot mode
    page.click(MODE_COPILOT)
    page.wait_for_load_state("networkidle")
    
    # Step 3: Ask a question
    page.fill(QUERY_INPUT, "What are total purchases")
    page.click(ASK_BUTTON)
    
    # Wait for results
    page.wait_for_selector(
        f"{RESULTS_TABLE}, {RESULTS_CONTAINER}",
        timeout=10000,
        state="visible"
    )
    
    # Step 4: Assert export button is visible
    assert page.is_visible(EXPORT_BUTTON), "Export button should be visible after results"
