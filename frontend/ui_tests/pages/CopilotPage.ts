import { Page, expect } from "@playwright/test";

/**
 * Page Object Model for Copilot UI
 * Encapsulates all selectors and interactions for the copilot page.
 */
export class CopilotPage {
  readonly page: Page;
  readonly baseUrl: string;

  // Selectors
  readonly modeToggleData = 'button:has-text("Data")';
  readonly modeToggleAIReports = 'button:has-text("AI Reports")';
  readonly modeToggleInsights = 'button:has-text("Insights")';
  readonly queryInput =
    'input[placeholder*="search"], input[placeholder*="query"], textarea, input[type="text"]';
  readonly askButton =
    'button:has-text("Ask"), button:has-text("Send"), button:has-text("Submit")';
  readonly resultsContainer =
    '[data-testid="results"], .results, .output, #results, .response';
  readonly resultTable = "table";
  readonly resultCard = '.card, [data-testid="result-card"], .card-body';
  readonly aiBadge = ':has-text("AI"), :has-text("Generated"), :has-text("Report")';
  readonly errorMessage = '.error, [role="alert"], .alert';

  constructor(page: Page) {
    this.page = page;
    this.baseUrl = "http://localhost:8000";
  }

  /**
   * Navigate to the copilot page
   */
  async navigate() {
    await this.page.goto(`${this.baseUrl}/`);
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad(timeout = 5000) {
    await this.page.waitForLoadState("networkidle", { timeout });
  }

  /**
   * Select "Data" mode
   */
  async selectDataMode() {
    const buttons = await this.page.locator("button").all();
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (text && text.toLowerCase().includes("data")) {
        await btn.click();
        return;
      }
    }
  }

  /**
   * Select "AI Reports" mode
   */
  async selectAIReportsMode() {
    const buttons = await this.page.locator("button").all();
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (
        text &&
        (text.toLowerCase().includes("ai") ||
          text.toLowerCase().includes("report"))
      ) {
        await btn.click();
        return;
      }
    }
  }

  /**
   * Select "Insights" mode
   */
  async selectInsightsMode() {
    const buttons = await this.page.locator("button").all();
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (text && text.toLowerCase().includes("insight")) {
        await btn.click();
        return;
      }
    }
  }

  /**
   * Enter query text in the input field
   */
  async enterQuery(queryText: string) {
    // Find text input or textarea
    const inputs = await this.page
      .locator(
        'input[type="text"], textarea, input:not([type]), input[placeholder]'
      )
      .all();

    if (inputs.length > 0) {
      await inputs[0].fill(queryText);
    } else {
      // Fallback: find any input
      const anyInput = this.page.locator("input").first();
      await anyInput.fill(queryText);
    }
  }

  /**
   * Click the "Ask" or "Send" button
   */
  async clickAskButton() {
    const buttons = await this.page.locator("button").all();
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (
        text &&
        (text.toLowerCase().includes("ask") ||
          text.toLowerCase().includes("send") ||
          text.toLowerCase().includes("submit"))
      ) {
        await btn.click();
        return;
      }
    }
    // Fallback: click first button if none matched
    if (buttons.length > 0) {
      await buttons[0].click();
    }
  }

  /**
   * Get the visible results text
   */
  async getResultsText(): Promise<string> {
    try {
      const text = await this.page.locator("body").textContent();
      return text || "";
    } catch {
      return "";
    }
  }

  /**
   * Check if results are displayed
   */
  async isResultsVisible(): Promise<boolean> {
    try {
      const selector = this.page.locator(
        '[data-testid="results"], .results, .output, #results, .response, table, .card'
      );
      const count = await selector.count();
      return count > 0;
    } catch {
      return false;
    }
  }

  /**
   * Check if results table is visible
   */
  async isTableVisible(): Promise<boolean> {
    try {
      const table = this.page.locator(this.resultTable);
      return (await table.count()) > 0;
    } catch {
      return false;
    }
  }

  /**
   * Check if AI badge or AI content is visible
   */
  async isAIBadgeVisible(): Promise<boolean> {
    try {
      const badges = await this.page
        .locator(
          'text="AI", text="Generated", text="Report", text="Analysis"'
        )
        .all();
      return badges.length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Get error message if displayed
   */
  async getErrorMessage(): Promise<string | null> {
    try {
      const error = await this.page.locator(this.errorMessage).textContent();
      return error;
    } catch {
      return null;
    }
  }

  /**
   * Wait for results to appear on page
   */
  async waitForResults(timeout = 10000) {
    // Wait for either results container, table, or any visible content
    try {
      await this.page
        .locator(
          "[data-testid=\"results\"], .results, .output, #results, table, .card"
        )
        .first()
        .waitFor({ state: "visible", timeout });
    } catch {
      // Even if specific selector not found, page may have rendered content
    }
  }

  /**
   * Set up route interception for API calls (call before navigate)
   */
  async setupRouteInterception() {
    // Intercept /copilot/ask
    await this.page.route("**/copilot/ask", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          intent: "list_purchase_orders",
          message: "Found 10 purchase orders.",
          data: [
            {
              name: "PO-2024-001",
              supplier: "Supplier A",
              grand_total: 5000.0,
              status: "Completed",
            },
            {
              name: "PO-2024-002",
              supplier: "Supplier B",
              grand_total: 7500.0,
              status: "Submitted",
            },
          ],
        }),
      });
    });

    // Intercept /ai/report
    await this.page.route("**/ai/report", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          report:
            "Monthly procurement analysis shows stable supplier performance.",
          summary: "Cost-effective purchasing with competitive rates.",
        }),
      });
    });
  }
}
