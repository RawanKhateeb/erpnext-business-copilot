# UI Tests

Playwright E2E tests for the ERPNext Copilot UI using Page Object Model (POM).

## Structure

```
frontend/ui_tests/
├── pages/
│   ├── CopilotPage.ts      # Page Object (selectors + methods)
│   └── __init__.ts
├── tests/
│   ├── e2e_user_journey.spec.ts # One E2E test
│   └── __init__.ts
├── playwright.config.ts    # Playwright config
├── package.json            # Node dependencies
└── README.md               # This file
```

## Installation

```bash
cd frontend/ui_tests

# Install Node dependencies
npm install

# Install Playwright browsers
npx playwright install --with-deps
```

## Running Tests

### Run All Tests
```bash
npx playwright test
```

### Run with UI (Interactive)
```bash
npx playwright test --ui
```

### Run in Headed Mode (See Browser)
```bash
npx playwright test --headed
```

### Run Specific Browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Run Specific Test
```bash
npx playwright test e2e_user_journey
```

### Debug Mode
```bash
npx playwright test --debug
```

### View HTML Report
```bash
npx playwright show-report
```

## Page Object Model (POM)

### CopilotPage.ts
Encapsulates all UI interactions:

**Methods**:
- `navigate()` - Go to copilot page
- `selectDataMode()` - Click "Data" button
- `selectAIReportsMode()` - Click "AI Reports" button
- `enterQuery(text)` - Type in query input
- `clickAskButton()` - Click "Ask" button
- `waitForResults()` - Wait for results to appear
- `isResultsVisible()` - Check if results shown
- `getResultsText()` - Get visible page text
- `setupRouteInterception()` - Mock API responses

**Why POM?**
- Selectors are centralized (easy to update)
- Tests are more readable (high-level methods)
- Maintenance is easier (change once, affects all tests)
- No raw selectors in test code

## API Route Interception

Tests mock API responses so NO real backend is needed:

```typescript
// Mock /copilot/ask
{
  "intent": "list_purchase_orders",
  "message": "Found 10 purchase orders.",
  "data": [{ "name": "PO-2024-001", ... }]
}

// Mock /ai/report
{
  "report": "Monthly procurement analysis...",
  "summary": "Cost-effective purchasing..."
}
```

This ensures:
- ✅ Tests are fast (no real DB/API calls)
- ✅ Tests are stable (no external dependencies)
- ✅ Tests can run offline
- ✅ Errors in backend don't break UI tests

## E2E User Journey Test

**File**: `tests/e2e_user_journey.spec.ts`

**Journey**:
1. Open Copilot page
2. Select "Data" mode
3. Type: "Show purchase orders"
4. Click Ask → Verify results (table or text with "purchase")
5. Switch to "AI Reports" mode
6. Type: "Generate monthly procurement report"
7. Click Ask → Verify AI results (text with "monthly", "report", or "analysis")

**Assertions**:
- Page title contains "Copilot" or "ERPNext"
- Results container is visible
- Results contain expected keywords
- No error messages shown

## Adding New Tests

1. Create new `.spec.ts` file in `tests/`
2. Use `CopilotPage` methods (not raw selectors)
3. Set up route interception before navigating
4. Use meaningful assertions

Example:
```typescript
import { test, expect } from "@playwright/test";
import { CopilotPage } from "../pages/CopilotPage";

test("My new test", async ({ page }) => {
  const copilotPage = new CopilotPage(page);
  
  // Setup mocks
  await copilotPage.setupRouteInterception();
  
  // Navigate
  await copilotPage.navigate();
  await copilotPage.waitForPageLoad();
  
  // Interact
  await copilotPage.selectDataMode();
  await copilotPage.enterQuery("suppliers");
  await copilotPage.clickAskButton();
  
  // Assert
  await copilotPage.waitForResults();
  const visible = await copilotPage.isResultsVisible();
  expect(visible).toBeTruthy();
});
```

## Configuration

**playwright.config.ts**:
- Base URL: `http://localhost:8000`
- Test directory: `./tests`
- Browsers: Chromium, Firefox, WebKit
- Retries in CI: 2
- Screenshots on failure
- HTML report generation
- Trace recording on first failure

## CI Integration

UI tests run automatically in GitHub Actions CI:
- ✅ No real backend required (mocked)
- ✅ No secrets needed
- ✅ Runs on every push/PR
- ✅ Generates HTML report

See `.github/workflows/ci.yml` for details.

## Troubleshooting

### Tests fail with "cannot find element"
- Check if page selectors have changed
- Update selectors in `CopilotPage.ts`
- Use `--debug` mode to inspect page

### Routes not being intercepted
- Ensure `setupRouteInterception()` is called BEFORE `navigate()`
- Check that route patterns match actual requests (use DevTools)

### Tests timeout
- Increase `waitForResults()` timeout
- Check if page renders correctly in headed mode: `--headed`
- View trace: Open HTML report and check traces

### Performance is slow
- Run single test: `npx playwright test --project=chromium e2e_user_journey`
- Disable other browsers in `playwright.config.ts` for faster iteration

## Key Guidelines

- ✅ Use POM pattern (selectors in Page Objects only)
- ✅ Mock all API responses
- ✅ Use high-level page methods in tests
- ✅ Keep tests readable and focused
- ✅ One test per user journey
- ✅ No hardcoded delays (use waitFor methods)
- ✅ Assertions should be clear
- ✅ Generate HTML reports for debugging

## Performance

- Per test: ~10-30s (depending on system)
- Goal: < 60s total for all UI tests
- CI: Runs serially (1 worker) for stability

---

See `docs/TEST_PLAN.md` for detailed test strategy.
