"""
Page Object Model for Copilot UI.
Encapsulates all selectors and interactions for the copilot page.
"""


class CopilotPage:
    """Page Object for the main Copilot UI page."""

    def __init__(self, page):
        """
        Initialize page object.
        
        Args:
            page: Playwright Page object
        """
        self.page = page
        self.base_url = "http://localhost:8000"

    # Selectors
    MODE_TOGGLE_DATA = 'button:has-text("Data")'
    MODE_TOGGLE_AI_REPORTS = 'button:has-text("AI Reports")'
    MODE_TOGGLE_INSIGHTS = 'button:has-text("Insights")'
    QUERY_INPUT = 'input[placeholder*="search"], input[placeholder*="query"], textarea'
    ASK_BUTTON = 'button:has-text("Ask"), button:has-text("Send")'
    RESULTS_CONTAINER = '[data-testid="results"], .results, .output'
    RESULT_TABLE = 'table'
    RESULT_CARD = '.card, [data-testid="result-card"]'
    AI_BADGE = ':has-text("AI"), :has-text("Generated")'
    ERROR_MESSAGE = '.error, [role="alert"]'

    # Methods
    async def navigate(self):
        """Navigate to the copilot page."""
        await self.page.goto(f"{self.base_url}/")

    async def wait_for_page_load(self, timeout=5000):
        """Wait for page to be fully loaded."""
        await self.page.wait_for_load_state("networkidle", timeout=timeout)

    async def select_data_mode(self):
        """Click the 'Data' mode toggle."""
        await self.page.click(self.MODE_TOGGLE_DATA)

    async def select_ai_reports_mode(self):
        """Click the 'AI Reports' mode toggle."""
        await self.page.click(self.MODE_TOGGLE_AI_REPORTS)

    async def select_insights_mode(self):
        """Click the 'Insights' mode toggle."""
        await self.page.click(self.MODE_TOGGLE_INSIGHTS)

    async def enter_query(self, query_text):
        """
        Enter query text in the input field.
        
        Args:
            query_text: Text to enter
        """
        # Find the input field (could be input or textarea)
        inputs = await self.page.query_selector_all(
            'input[type="text"], textarea, input[placeholder*="search"], input[placeholder*="query"]'
        )
        if inputs:
            await inputs[0].fill(query_text)
        else:
            # Fallback: click first text input on page
            await self.page.fill('input', query_text)

    async def click_ask_button(self):
        """Click the 'Ask' or 'Send' button."""
        buttons = await self.page.query_selector_all('button')
        for btn in buttons:
            text = await btn.text_content()
            if text and ('ask' in text.lower() or 'send' in text.lower()):
                await btn.click()
                return
        # Fallback: click the first button
        if buttons:
            await buttons[0].click()

    async def get_results_text(self):
        """Get the visible results text from the page."""
        # Try to get text from results container
        try:
            text = await self.page.text_content(self.RESULTS_CONTAINER)
            return text
        except:
            # Fallback: get all visible text
            return await self.page.text_content("body")

    async def is_results_visible(self):
        """Check if results are displayed."""
        try:
            result = await self.page.query_selector(self.RESULTS_CONTAINER)
            return result is not None
        except:
            return False

    async def is_table_visible(self):
        """Check if results table is visible."""
        try:
            table = await self.page.query_selector(self.RESULT_TABLE)
            return table is not None
        except:
            return False

    async def is_ai_badge_visible(self):
        """Check if 'AI Generated' or similar badge is visible."""
        try:
            badge = await self.page.query_selector(self.AI_BADGE)
            return badge is not None
        except:
            return False

    async def get_error_message(self):
        """Get error message if displayed."""
        try:
            error = await self.page.text_content(self.ERROR_MESSAGE)
            return error
        except:
            return None

    async def wait_for_results(self, timeout=10000):
        """Wait for results to appear on page."""
        await self.page.wait_for_selector(
            self.RESULTS_CONTAINER, timeout=timeout, state="visible"
        )

    async def route_api_response(self, endpoint, response_json):
        """
        Mock an API response using route interception.
        
        Args:
            endpoint: The API endpoint path (e.g., "/copilot/ask")
            response_json: The JSON response to return
        """
        async def handle_route(route):
            await route.abort()

        # Intercept the endpoint and return mocked response
        await self.page.route(
            f"**/api/**{endpoint}",
            lambda route: self._mock_response(route, response_json),
        )

    async def _mock_response(self, route, response_json):
        """Helper to mock API response."""
        await route.abort()
        await route.continue_()

    async def intercept_api_calls(self):
        """
        Set up route interception for API calls.
        Must be called before navigating to page.
        """
        # Intercept /copilot/ask
        await self.page.route(
            "**/copilot/ask",
            self._handle_copilot_ask,
        )
        # Intercept /ai/report
        await self.page.route(
            "**/ai/report",
            self._handle_ai_report,
        )

    async def _handle_copilot_ask(self, route):
        """Handle mocked /copilot/ask response."""
        response_data = {
            "intent": "list_purchase_orders",
            "message": "Found 10 purchase orders.",
            "data": [
                {
                    "name": "PO-2024-001",
                    "supplier": "Supplier A",
                    "grand_total": 5000.00,
                    "status": "Completed",
                }
            ],
        }
        await route.fulfill(
            status=200,
            content_type="application/json",
            body_json=response_data,
        )

    async def _handle_ai_report(self, route):
        """Handle mocked /ai/report response."""
        response_data = {
            "report": "Monthly procurement analysis shows stable supplier performance.",
            "summary": "Cost-effective purchasing with competitive rates.",
        }
        await route.fulfill(
            status=200,
            content_type="application/json",
            body_json=response_data,
        )
