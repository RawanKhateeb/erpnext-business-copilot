# Backend Tests

Mock tests for ERPNext Copilot backend endpoints using Python `unittest`.

## Quick Start

### Run Mock Tests (No Dependencies)
```bash
cd backend
python -m unittest discover tests/api_mock -v
```

**Expected**: ~35+ tests pass in ~500ms ✅

### Run Integration Tests (Local ERPNext only)
```bash
export ERP_URL=http://localhost:8080
export ERP_API_KEY=your_key
cd backend
python -m unittest discover tests/api_integration_local -v
```

**Expected**: Auto-skips if ERP_URL not set ✅

## Structure

```
backend/tests/
├── api_mock/                      # Mock tests (no external dependencies)
│   ├── base_test.py              # Base test class
│   ├── mock_data.py              # Mock data
│   ├── test_suppliers.py
│   ├── test_purchase_orders.py
│   ├── test_copilot_ask.py
│   └── test_ai_report.py
└── api_integration_local/         # Integration tests (real ERPNext only)
    └── test_endpoints.py
```

## Test Coverage

- ✅ 35+ mock tests (happy path + error path)
- ✅ GET /suppliers, GET /items
- ✅ GET /purchase-orders (with limit param)
- ✅ GET /purchase-orders/{po_name}
- ✅ POST /copilot/ask (intent recognition)
- ✅ POST /ai/report (with OpenAI error handling)

---

**📖 For comprehensive documentation, see [docs/TEST_PLAN.md](../../docs/TEST_PLAN.md)**
