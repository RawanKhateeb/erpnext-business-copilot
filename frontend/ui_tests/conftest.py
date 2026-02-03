"""Pytest configuration for Playwright UI tests."""
import os
import pytest
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
def browser() -> Browser:
    """Create a browser instance for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def context(browser: Browser) -> BrowserContext:
    """Create a browser context for the test session."""
    context = browser.new_context(ignore_https_errors=True)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()

