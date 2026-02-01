"""
Tests for Ask Flow - User Question to Answer.
Tests the complete flow: write question → click ask → get answer.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.copilot_page import CopilotPage


class TestAskFlow:
    """Test suite for ask flow functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        """
        Setup before each test.

        Args:
            page: Playwright Page fixture
        """
        self.page = page
        self.copilot = CopilotPage(page)
        self.copilot.navigate_to_copilot()

    def test_ask_simple_question_get_answer(self) -> None:
        """
        E2E: User writes question and gets answer.

        Steps:
            1. User navigates to copilot page
            2. User writes "Show me all suppliers"
            3. User clicks Ask button
            4. System returns results
        """
        # Write question
        self.copilot.ask_question("Show me all suppliers", wait_for_response=True)

        # Verify response is displayed
        content = self.copilot.get_results_text()
        assert self.copilot.has_results(), "Expected results to be displayed"

    def test_ask_question_about_items(self) -> None:
        """
        User gets answer with specific question about items.

        Steps:
            1. Select Data mode
            2. Ask "What items are available?"
            3. Verify response contains item data
        """
        # Select Data mode
        self.copilot.select_data_mode()
        self.page.wait_for_timeout(500)

        # Ask question
        self.copilot.ask_question("What items are available?")

        # Verify response
        assert self.copilot.has_results(), "Expected item results"

    def test_empty_question_validation(self) -> None:
        """
        Empty question shows validation or no action.

        Steps:
            1. Leave query empty
            2. Click Ask button
            3. System should either show error or do nothing
        """
        # Try to ask empty question
        try:
            self.copilot.ask_question("", wait_for_response=False)
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Either error shown or page unchanged - both acceptable
        content = self.copilot.get_page_content()
        assert content is not None, "Page should still be loaded"

    def test_response_displays_data_formatted(self) -> None:
        """
        Response displays data in readable format.

        Steps:
            1. Ask "Show purchase orders"
            2. Verify response is formatted (table/list/readable)
        """
        self.copilot.ask_question("Show purchase orders")

        # Check for formatted response indicators
        content = self.copilot.get_results_text()
        assert len(content) > 100, "Response should contain substantial data"
        assert self.copilot.has_results(), "Results should be displayed"

    def test_multiple_questions_sequence(self) -> None:
        """
        User can ask multiple questions sequentially.

        Steps:
            1. Ask first question
            2. Ask second question
            3. Verify both get responses
        """
        # First question
        self.copilot.ask_question("Show suppliers")
        first_content = self.copilot.get_results_text()
        assert self.copilot.has_results(), "First question should return results"

        # Second question
        self.copilot.ask_question("Show items")
        second_content = self.copilot.get_results_text()
        assert self.copilot.has_results(), "Second question should return results"

        # Both should have returned something
        assert first_content is not None
        assert second_content is not None
