# Test Plan for ERPNext Copilot

## Overview

This document describes the automated testing strategy for the ERPNext Copilot mono-repo project (frontend + backend). The testing approach follows class guidelines:

- **Backend tests**: Python `unittest` (NOT pytest)
- **UI tests**: Playwright with Page Object Model (POM)
- **Integration tests**: Run LOCALLY ONLY (not in GitHub Actions)
- **CI**: Runs mock tests and UI tests only

---

## Testing Structure

```
project/
├── backend/tests/
│   ├── api_mock/                 # Skill-only backend tests (mock ERPNext + OpenAI)
│   │   ├── __init__.py
│   │   ├── base_test.py          # Base class for all API tests
│   │   ├── mock_data.py          # Mock data (suppliers, POs, etc.)
│   │   ├── test_suppliers.py     # Tests for /suppliers endpoint
│   │   ├── test_purchase_orders.py # Tests for /purchase-orders endpoints
│   │   ├── test_copilot_ask.py   # Tests for /copilot/ask endpoint
│   │   └── test_ai_report.py     # Tests for /ai/report endpoint
│   │
│   └── api_integration_local/    # Integration tests (real ERPNext) - local only
│       ├── __init__.py
│       └── test_endpoints.py     # Smoke tests against real ERPNext
│
├── frontend/ui_tests/
│   ├── pages/
│   │   ├── CopilotPage.ts        # Page Object for Copilot UI
│   │   └── __init__.ts
│   ├── tests/
│   │   ├── e2e_user_journey.spec.ts # One E2E user journey
│   │   └── __init__.ts
│   ├── playwright.config.ts      # Playwright configuration
│   └── package.json              # Node dependencies
│
├── .github/workflows/
│   └── ci.yml                    # GitHub Actions CI pipeline
│
└── docs/
    └── TEST_PLAN.md              # This file
```

---

## Backend Tests

### Mock API Tests (Skill-only)

**Location**: `backend/tests/api_mock/`

**Purpose**: Test backend endpoints WITHOUT calling real ERPNext or OpenAI.

**Tools**:
- `unittest` framework (standard library)
- FastAPI `TestClient` for HTTP requests
- `unittest.mock` for mocking external services

**Test Files**:

1. **test_suppliers.py** - Tests `/suppliers` endpoint
   - Happy path: returns 200 with supplier list
   - Response structure: verifies expected JSON keys
   - Error path: returns 500 when client fails

2. **test_purchase_orders.py** - Tests `/purchase-orders` and `/purchase-orders/{po_name}` endpoints
   - Happy path: returns 200 with PO list
   - Parameter handling: limit parameter is respected
   - Detail endpoint: returns single PO data
   - Error path: graceful error handling

3. **test_copilot_ask.py** - Tests `/copilot/ask` endpoint
   - Intent recognition: supplier queries, PO queries
   - Parameter validation: missing/empty query handled
   - Response structure: contains message and data fields
   - Error path: client exceptions handled gracefully

4. **test_ai_report.py** - Tests `/ai/report` endpoint
   - Happy path: generates report with mocked OpenAI
   - Response structure: report and summary fields present
   - Error path: OpenAI API failure handled gracefully
   - Network error: connection failures handled

**Mock Data**: `mock_data.py`
- `MOCK_SUPPLIERS`: 3 sample suppliers
- `MOCK_ITEMS`: 2 sample items
- `MOCK_PURCHASE_ORDERS`: 3 sample POs
- `MOCK_PURCHASE_ORDER_DETAIL`: Detail of one PO
- `MOCK_AI_REPORT`: Sample AI report

**Base Class**: `base_test.py`
- `APITestBase`: Provides test client setup, assertion helpers
- `mock_erpnext_client()`: Helper to mock ERPNext client

**Coverage Goals**:
- Happy paths (200 responses with correct data)
- Error paths (missing params, client failures)
- Parameter validation
- Response structure validation

**How to Run**:
```bash
cd backend
python -m unittest discover tests/api_mock -v
```

**Expected Output**:
```
test_ai_report_empty_query (test_ai_report.TestAIReportEndpoint) ... ok
test_ai_report_handles_openai_api_error (test_ai_report.TestAIReportEndpoint) ... ok
test_ai_report_returns_200_with_report (test_ai_report.TestAIReportEndpoint) ... ok
... (multiple tests)
Ran 35 tests in 0.125s
OK
```

---

### Integration API Tests (Local Only)

**Location**: `backend/tests/api_integration_local/`

**Purpose**: Smoke tests against REAL ERPNext running locally.

**Important**: These tests are SKIPPED automatically if:
- `ERP_URL` environment variable is not set
- `ERP_API_KEY` environment variable is not set

These tests do NOT run in GitHub Actions CI.

**Test File**: `test_endpoints.py`

**Smoke Tests**:
1. `/suppliers` returns 200 with data list
2. `/purchase-orders` returns 200 with data list
3. `/purchase-orders/{po_name}` returns 200 for valid PO

**How to Run Locally** (when ERPNext is running):
```bash
export ERP_URL="http://localhost:8080"
export ERP_API_KEY="your_api_key"

cd backend
python -m unittest discover tests/api_integration_local -v
```

**How to Run without ERPNext** (will be skipped):
```bash
cd backend
python -m unittest discover tests/api_integration_local -v
# Output: Skipped - ERP_URL or ERP_API_KEY not set
```

---

## UI Tests

### Playwright with Page Object Model

**Location**: `frontend/ui_tests/`

**Purpose**: End-to-end UI testing using Playwright and Page Object Model (POM).

**Approach**:
- Route interception to mock API responses (no real backend calls)
- Page Object encapsulates all selectors and interactions
- One E2E user journey test

**Page Object**: `pages/CopilotPage.ts`

**Responsibilities**:
- Encapsulate all CSS/XPath selectors
- Provide high-level methods: `selectDataMode()`, `enterQuery()`, `clickAskButton()`
- Handle route interception and mocking
- Provide assertions: `isResultsVisible()`, `isTableVisible()`, `isAIBadgeVisible()`

**Key Methods**:
- `navigate()`: Go to copilot page
- `selectDataMode()`: Click Data toggle
- `selectAIReportsMode()`: Click AI Reports toggle
- `enterQuery(text)`: Type in query input
- `clickAskButton()`: Click Ask/Send button
- `waitForResults()`: Wait for results to appear
- `isResultsVisible()`: Check if results displayed
- `getResultsText()`: Get visible text on page
- `setupRouteInterception()`: Mock API calls

**Route Interception**:
Mocks `/copilot/ask` and `/ai/report` endpoints:
```typescript
// GET /copilot/ask
Response: {
  "intent": "list_purchase_orders",
  "message": "Found 10 purchase orders.",
  "data": [{ "name": "PO-2024-001", ... }]
}

// POST /ai/report
Response: {
  "report": "Monthly procurement analysis...",
  "summary": "Cost-effective purchasing..."
}
```

**E2E Test**: `tests/e2e_user_journey.spec.ts`

**User Journey**:
1. Open Copilot page
2. Verify page loaded
3. Select "Data" mode
4. Type: "Show purchase orders"
5. Click Ask
6. Verify results appear (table or text)
7. Switch to "AI Reports" mode
8. Type: "Generate monthly procurement report"
9. Click Ask
10. Verify AI report appears

**Assertions**:
- Page title contains "Copilot" or "ERPNext"
- Results container visible
- Results contain "purchase" or supplier data
- AI results contain "monthly", "report", or "analysis"

**Configuration**: `playwright.config.ts`
- Test directory: `./tests`
- Base URL: `http://localhost:8000`
- Browsers: Chromium, Firefox, WebKit
- Screenshots on failure
- HTML report generation

**How to Install**:
```bash
cd frontend/ui_tests
npm install
npx playwright install --with-deps
```

**How to Run**:
```bash
cd frontend/ui_tests
# Run all tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific project (browser)
npx playwright test --project=chromium

# View HTML report
npx playwright show-report
```

---

## GitHub Actions CI

**File**: `.github/workflows/ci.yml`

**Trigger**: Push or Pull Request to `main` or `develop` branches

**Jobs**:

### 1. Backend Mock Tests
- Runs `backend/tests/api_mock` tests
- Uses Python 3.11
- NO dependencies on ERPNext, OpenAI, or environment variables
- Status: REQUIRED

### 2. UI Tests (Playwright)
- Runs `frontend/ui_tests` tests
- Uses Node.js 18 and Python 3.11
- NO dependencies on real ERPNext or OpenAI
- All API responses are mocked
- Generates HTML report
- Status: REQUIRED

### 3. Test Summary
- Prints overall status
- Fails if any job failed

**Excluded from CI**:
- ❌ Integration tests (`backend/tests/api_integration_local`)
- ❌ Real ERPNext calls
- ❌ Real OpenAI calls
- ❌ Secrets or API keys

**How to View Results**:
1. Go to GitHub Actions tab
2. Click on workflow run
3. View test logs
4. Download Playwright report artifact

---

## Success Criteria

### All Tests Pass
- ✅ Backend mock tests: All assertions pass
- ✅ UI tests: All assertions pass
- ✅ CI: Green checkmark on PR

### Local Integration Tests Pass (when ERPNext is running)
```bash
export ERP_URL="http://localhost:8080"
export ERP_API_KEY="your_key"
cd backend
python -m unittest discover tests/api_integration_local -v
# Output: OK
```

### Code Quality
- Tests are isolated (mock external dependencies)
- Tests are fast (< 1 second per test for backend)
- Tests are readable (descriptive names, clear assertions)
- No duplicated test code (use base classes)

---

## Failure Scenarios

### Backend Tests Fail
- Check mock data in `mock_data.py`
- Verify endpoint implementation in `app/main.py`
- Ensure all mocks are patched correctly

### UI Tests Fail
- Check if page selectors have changed
- Update selectors in `CopilotPage.ts`
- Verify route interception is working
- Check Playwright report for screenshots/traces

### Integration Tests Skip
- Expected if `ERP_URL` or `ERP_API_KEY` not set
- Set environment variables to run:
  ```bash
  export ERP_URL="http://localhost:8080"
  export ERP_API_KEY="your_key"
  ```

---

## Maintenance

### Adding New Tests

**Backend Mock Test**:
1. Create new file `test_new_endpoint.py` in `backend/tests/api_mock/`
2. Inherit from `APITestBase`
3. Add mock data to `mock_data.py`
4. Test happy path, error path, parameter validation

Example:
```python
from base_test import APITestBase
from mock_data import MOCK_ITEMS

class TestItemsEndpoint(APITestBase):
    def test_items_returns_200(self):
        mock_client = MagicMock()
        mock_client.list_items.return_value = MOCK_ITEMS
        
        with patch('app.main.get_client', return_value=mock_client):
            response = self.client.get("/items")
        
        self.assert_response_ok(response)
```

**UI Test**:
1. Add new test in `frontend/ui_tests/tests/`
2. Add new page methods in `CopilotPage.ts` if needed
3. Use existing route interception

---

## Performance

### Backend Tests
- Typical runtime: 100-500ms
- Goal: < 1s total for all mock tests

### UI Tests
- Typical runtime: 10-30s per test
- Goal: < 60s total for all UI tests

### CI Pipeline
- Backend tests: ~30s
- UI tests: ~60s
- Total: ~90s

---

## Environment Variables

### For Local Integration Tests
```bash
ERP_URL=http://localhost:8080  # ERPNext base URL
ERP_API_KEY=your_api_key        # ERPNext API key
```

### For CI/Mock Tests
Not required. Tests use mocked responses.

---

## Cleanup / Teardown

All tests clean up properly:
- Mock patches are automatically removed
- No database changes
- No real API calls
- No temporary files created

---

## References

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [FastAPI TestClient](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [Playwright documentation](https://playwright.dev/)
- [Playwright POM pattern](https://playwright.dev/docs/pom)
- [GitHub Actions documentation](https://docs.github.com/en/actions)

---

**Last Updated**: January 2026
