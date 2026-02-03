"""
Page Object Model for Copilot UI.
Encapsulates all selectors and interactions for the copilot page.
"""

from playwright.sync_api import Page
from .base_page import BasePage


class CopilotPage(BasePage):
    """Page Object for the main Copilot UI page."""

    # Selectors as class constants
    MODE_BUTTON_DATA = "button"  # Will use get_by_role
    ASK_BUTTON = "button"  # Will use get_by_role
    QUERY_INPUT_PLACEHOLDER = "ask"
    RESULTS_CONTAINER = ".results"
    RESULT_TABLE = "table"
    ERROR_MESSAGE = "[role='alert']"
    EXPORT_BUTTON = "button"  # Will use get_by_role

    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8000") -> None:
        """
        Initialize Copilot page object.

        Args:
            page: Playwright Page instance
            base_url: Base URL for the application
        """
        super().__init__(page, base_url)

    def navigate_to_copilot(self) -> None:
        """Navigate to the copilot page."""
        self.navigate("/")
        # Wait for page to load (use load instead of networkidle to avoid hanging)
        self.page.wait_for_load_state("load", timeout=5000)

    def select_data_mode(self) -> None:
        """Click the 'Data' mode button."""
        try:
            self.click_by_role("button", "Data")
        except Exception:
            # Button might not exist or be already selected
            pass

    def select_ai_reports_mode(self) -> None:
        """Click the 'AI Reports' mode button."""
        try:
            self.click_by_role("button", "AI Reports")
        except Exception:
            pass

    def select_insights_mode(self) -> None:
        """Click the 'Insights' mode button."""
        try:
            self.click_by_role("button", "Insights")
        except Exception:
            pass

    def ask_question(self, query: str, wait_for_response: bool = True) -> None:
        """
        Write a question and click ask.

        Args:
            query: Question to ask
            wait_for_response: Wait for response to appear
        """
        # Fill the query input
        try:
            # Try to find input by placeholder
            self.page.get_by_placeholder("ask", exact=False).fill(query)
        except Exception:
            # Fallback: find any text input and fill it
            inputs = self.page.locator("input[type='text'], textarea")
            if inputs.count() > 0:
                inputs.first.fill(query)

        # Click ask button
        try:
            self.click_by_role("button", "Ask")
        except Exception:
            self.click_by_text("Ask")

        # Wait for response if requested
        if wait_for_response:
            self.wait_for_response()

    def wait_for_response(self, timeout: int = 10000) -> None:
        """
        Wait for response to appear after asking.

        Args:
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_timeout(2000)  # Give API time to respond

    def get_results_text(self) -> str:
        """
        Get the text content of results.

        Returns:
            Results text content
        """
        content = self.get_page_content()
        return content if content else ""

    def has_results(self) -> bool:
        """
        Check if results are displayed.

        Returns:
            True if results visible
        """
        content = self.get_results_text()
        return any(keyword in content.lower() for keyword in ["supplier", "item", "data", "result"])

    def has_error(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error visible
        """
        return self.is_visible(self.ERROR_MESSAGE)

    def get_error_message(self) -> str | None:
        """
        Get error message text.

        Returns:
            Error message or None
        """
        if self.has_error():
            return self.get_text_content(self.ERROR_MESSAGE)
        return None

    def find_export_button(self) -> bool:
        """
        Look for export/download button.

        Returns:
            True if export button found
        """
        buttons = self.page.locator("button")
        for i in range(buttons.count()):
            button = buttons.nth(i)
            text = button.text_content() or ""
            if any(keyword in text.lower() for keyword in ["export", "download", "csv", "save"]):
                return True
        return False

    def click_export_button(self) -> bool:
        """
        Find and click export button.

        Returns:
            True if button was clicked
        """
        buttons = self.page.locator("button")
        for i in range(buttons.count()):
            button = buttons.nth(i)
            text = button.text_content() or ""
            if any(keyword in text.lower() for keyword in ["export", "download", "csv"]):
                button.click()
                return True
        return False

    def get_table_data(self) -> str | None:
        """
        Get table content if present.

        Returns:
            Table text content or None
        """
        if self.page.locator(self.RESULT_TABLE).count() > 0:
            return self.get_text_content(self.RESULT_TABLE)
        return None

    def is_page_loaded(self) -> bool:
        """
        Check if page is fully loaded.

        Returns:
            True if page is loaded
        """
        try:
            self.wait_for_load_state("networkidle", timeout=3000)
            return True
        except Exception:
            return False
