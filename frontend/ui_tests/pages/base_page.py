"""
Base Page Object for Playwright UI automation.
Provides common functionality for all page objects.
"""

from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects using Playwright Sync API."""

    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:8001") -> None:
        """
        Initialize page object.

        Args:
            page: Playwright Page instance
            base_url: Base URL for the application
        """
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "/") -> None:
        """
        Navigate to a URL.

        Args:
            path: URL path (relative to base_url)
        """
        url = f"{self.base_url}{path}"
        self.page.goto(url)

    def wait_for_url(self, pattern: str, timeout: int = 5000) -> None:
        """
        Wait for URL to match pattern.

        Args:
            pattern: URL pattern to match
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_url(pattern, timeout=timeout)

    def wait_for_load_state(self, state: str = "networkidle", timeout: int = 5000) -> None:
        """
        Wait for page load state.

        Args:
            state: Load state ("load", "domcontentloaded", "networkidle")
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_load_state(state, timeout=timeout)

    def wait_for_selector(self, selector: str, timeout: int = 5000) -> None:
        """
        Wait for element to be visible.

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).wait_for(timeout=timeout, state="visible")

    def click_by_role(self, role: str, name: str) -> None:
        """
        Click element by role and name.

        Args:
            role: ARIA role (button, textbox, etc.)
            name: Element name/text
        """
        self.page.get_by_role(role, name=name).click()

    def fill_by_role(self, role: str, name: str, text: str) -> None:
        """
        Fill input by role and name.

        Args:
            role: ARIA role (textbox, searchbox, etc.)
            name: Element name
            text: Text to enter
        """
        self.page.get_by_role(role, name=name).fill(text)

    def fill_by_placeholder(self, placeholder: str, text: str) -> None:
        """
        Fill input by placeholder.

        Args:
            placeholder: Placeholder text
            text: Text to enter
        """
        self.page.get_by_placeholder(placeholder).fill(text)

    def click_by_text(self, text: str) -> None:
        """
        Click element containing text.

        Args:
            text: Text to match
        """
        self.page.locator(f'button:has-text("{text}")').first.click()

    def get_text_content(self, selector: str) -> str | None:
        """
        Get text content of element.

        Args:
            selector: CSS selector

        Returns:
            Text content or None
        """
        return self.page.locator(selector).text_content()

    def is_visible(self, selector: str) -> bool:
        """
        Check if element is visible.

        Args:
            selector: CSS selector

        Returns:
            True if visible
        """
        return self.page.locator(selector).is_visible()

    def get_page_content(self) -> str:
        """
        Get full page content.

        Returns:
            Page HTML content
        """
        return self.page.content()

    def wait_for_element_count(self, selector: str, count: int, timeout: int = 5000) -> None:
        """
        Wait for specific number of elements.

        Args:
            selector: CSS selector
            count: Expected count
            timeout: Timeout in milliseconds
        """
        expect(self.page.locator(selector)).to_have_count(count, timeout=timeout)
