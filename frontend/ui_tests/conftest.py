"""
Pytest configuration for Playwright tests.
Provides fixtures and configuration for all tests.
"""

import pytest
from playwright.sync_api import sync_playwright, Browser, Page


@pytest.fixture(scope="session")
def browser() -> Browser:
    """
    Create a browser instance for the session.

    Yields:
        Browser instance
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser) -> Page:
    """
    Create a page instance for each test.

    Args:
        browser: Browser fixture

    Yields:
        Page instance
    """
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(autouse=True)
def test_setup(page: Page) -> None:
    """
    Setup before each test.

    Args:
        page: Page fixture
    """
    # Add any test setup here
    pass
