import { test, expect } from "@playwright/test";
import { CopilotPage } from "../pages/CopilotPage";

test.describe("Copilot User Journey", () => {
  test.beforeEach(async ({ page }) => {
    const copilotPage = new CopilotPage(page);

    // Set up route interceptions before navigating
    await copilotPage.setupRouteInterception();

    // Navigate to the app
    await copilotPage.navigate();
    await copilotPage.waitForPageLoad();
  });

  test("E2E User Journey: Data Query -> Ask -> AI Report", async ({
    page,
  }) => {
    const copilotPage = new CopilotPage(page);

    // Step 1: Verify we're on the page
    await expect(page).toHaveTitle(/Copilot|ERPNext/i);

    // Step 2: Select "Data" mode
    await copilotPage.selectDataMode();
    await page.waitForTimeout(500); // Brief wait for mode switch

    // Step 3: Type a query in Data mode
    await copilotPage.enterQuery("Show purchase orders");

    // Step 4: Click Ask button
    await copilotPage.clickAskButton();

    // Step 5: Verify results are shown (table or text containing purchase orders)
    await copilotPage.waitForResults(10000);
    const resultsVisible = await copilotPage.isResultsVisible();
    expect(resultsVisible).toBeTruthy();

    // Verify results contain purchase order data
    const resultsText = await copilotPage.getResultsText();
    const hasTableOrData =
      (await copilotPage.isTableVisible()) ||
      resultsText.toLowerCase().includes("purchase") ||
      resultsText.toLowerCase().includes("supplier");
    expect(hasTableOrData).toBeTruthy();

    // Step 6: Switch to "AI Reports" mode
    await copilotPage.selectAIReportsMode();
    await page.waitForTimeout(500); // Brief wait for mode switch

    // Step 7: Type a query for AI report
    await copilotPage.enterQuery("Generate monthly procurement report");

    // Step 8: Click Ask button
    await copilotPage.clickAskButton();

    // Step 9: Verify AI report is displayed
    await copilotPage.waitForResults(10000);
    const aiResultsVisible = await copilotPage.isResultsVisible();
    expect(aiResultsVisible).toBeTruthy();

    // Verify AI badge or AI report text is present
    const aiText = await copilotPage.getResultsText();
    const hasAIContent =
      (await copilotPage.isAIBadgeVisible()) ||
      aiText.toLowerCase().includes("monthly") ||
      aiText.toLowerCase().includes("report") ||
      aiText.toLowerCase().includes("analysis");
    expect(hasAIContent).toBeTruthy();
  });
});
