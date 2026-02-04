"""Pytest configuration for Playwright UI tests."""
import os
import pytest
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
def browser() -> Browser:
    """Create a browser instance for the test session."""

    # אם רץ ב-CI → headless
    headless = os.getenv("CI", "false").lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def context(browser: Browser) -> BrowserContext:
    """Create a browser context for the test session."""

    context = browser.new_context(
        ignore_https_errors=True,

        # עוקף אזהרת ngrok
        extra_http_headers={
            "ngrok-skip-browser-warning": "true"
        },

        # מאפשר הורדות PDF
        accept_downloads=True,
    )

    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""

    page = context.new_page()
    yield page
    page.close()
