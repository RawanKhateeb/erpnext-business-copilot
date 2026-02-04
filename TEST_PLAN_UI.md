# Test Plan – UI End-to-End Tests
## ERPNext Business Copilot

---

## What to Test

### Core User Scenarios

#### Scenario: Data Query → Results

- Happy path:
  Open application via BASE_URL (Ngrok) → Select Data mode → Enter query → Click Ask → Results displayed.

- Edge case:
  No matching data → "No results" message displayed.

- Failure:
  Backend unavailable → Error notification shown.

---

#### Scenario: Export PDF

- Happy path:
  After results → Click "Export as PDF" → PDF downloaded successfully.

- Failure:
  Export button disabled / export fails → Error message displayed.

---

## Test Design Strategy

- Implemented using Playwright with pytest.
- Tests executed in headless Chromium mode.
- Stable selectors used (roles / data-testid).
- Avoid fragile text-based assertions.
- Explicit waits for network and UI readiness.
- Screenshots captured automatically on failure.

---

## Test Environment

### Local
- Python 3.11
- Playwright (Chromium)
- Ngrok tunnel
- BASE_URL configured

### CI (GitHub Actions)
- Ubuntu runners
- Headless Chromium
- BASE_URL injected via environment variable
- Isolated execution environment

---

## External Dependencies

| Service | Purpose |
|---------|---------|
| Ngrok | Expose application |
| Allure | UI reporting |

---

## Success Criteria

### Stability
- No flaky tests in CI.
- Consistent execution results.


### Reliability
- PDF downloads validated correctly.

---

## Reporting

### Allure (UI Test Reports)

All UI tests generate Allure results providing:

- Step-by-step execution history
- Screenshots for failed tests
- Error logs and traces
- Trend analysis
- Historical comparison

**Local execution example:**
```bash
pytest frontend/ui_tests -v --alluredir=allure-results
allure serve allure-results
