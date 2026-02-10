# Test Plan – API Mock & Integration Tests
## ERPNext Business Copilot

---

## What to Test

### API Mock Tests (Controllers)

#### Endpoints
> Replace examples with actual endpoints if needed.

**GET /api/data/query**
- Happy path: valid query → returns structured JSON data.
- Validation: missing/invalid parameters → returns 400.
- Failure: internal processing error → returns 500.
- Edge case: no matching records → returns 200 with empty list.

**POST /api/ai/ask**
- Happy path: valid prompt → returns AI-generated response.
- Validation: empty prompt → returns 400.
- Edge case: low-confidence response → returns fallback output.

**POST /api/export/pdf**
- Happy path: valid report data → returns PDF stream.
- Validation: missing fields → returns 400.
- Failure: PDF generation error → returns 500.



---

### Integration Tests (ERPNext)

#### ERP Connectivity
- Happy path: valid ERP_URL and ERP_API_KEY → successful connection.
- Not configured: missing credentials → tests are skipped.

#### Real Data Validation
- Validate real ERP endpoints (suppliers, purchase orders, invoices).
- Verify response structure and required fields.
- Validate data types and formats.
- Handle empty datasets correctly.
- Validate error responses from ERP.

---

## Test Design Strategy

### API Mock Tests
- Implemented using pytest.
- External ERP calls are mocked.
- Focus on controller logic, validation, response schema, and error handling.
- Deterministic and CI-safe.

### Integration Tests
- Use real ERPNext endpoints.
- Executed only when credentials are available.
- Skipped automatically if ERP configuration is missing.
- Validate real end-to-end backend behavior.

---

## Test Environment

### Local
- Python 3.11
- Pytest
- Mocked ERP responses
- Optional real ERP credentials

### CI (GitHub Actions)
- Ubuntu runners
- API mock tests always executed
- Integration tests skipped if credentials missing (or run only in a secure environment)

---

## Success Criteria

### Coverage
- Backend coverage target: **90%+** (Codecov enforced)

### Stability
- All API mock tests must pass consistently.
- Integration tests must not break CI when credentials are missing (skip mechanism).

### Endpoint Coverage
Each endpoint must include:
- Happy-path test
- Negative test
- Edge-case test (where relevant)

---

## Reporting

### Allure (for ALL tests)
All API Mock + Integration tests generate Allure results to provide:
- Clear pass/fail reporting
- Failure stack traces
- History and trends
- Easy debugging of failing test cases

**Local execution (example):**
```bash
pytest backend/tests/api_mock -v --alluredir=allure-results
pytest backend/tests/integration -v --alluredir=allure-results
allure serve allure-results
