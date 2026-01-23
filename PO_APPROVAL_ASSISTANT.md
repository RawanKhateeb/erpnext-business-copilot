# ERPNext Procurement Approval Assistant

## Overview
Intelligent procurement approval module that analyzes purchase orders and provides APPROVE/REVIEW/DO NOT APPROVE recommendations based on price reasonability, supplier risk, and historical data.

## Features

### 1. **Smart Intent Recognition**
- Recognizes approval queries: "Should I approve PUR-ORD-2026-00001?"
- Extracts PO name automatically from natural language
- Supports variations: "Can I approve...", "Should I approve...", etc.

### 2. **Price Reasonability Check**
- Compares item unit rates to historical averages from past purchase orders
- Flags items with prices >= 20% above average as anomalies
- Highlights missing historical data for better decision-making

### 3. **Supplier Risk Assessment**
- Counts open/pending orders per supplier
- Flags if supplier has 3+ open orders (indicates backlog risk)
- Identifies pricing trends across supplier's order history

### 4. **Decision Logic**
```
APPROVE        → No anomalies, no high risks
REVIEW         → Moderate risks or missing data requiring attention
DO NOT APPROVE → Clear price anomalies and/or high supplier risk
```

### 5. **Detailed Evidence**
Returns structured analysis with:
- **Summary**: PO details (supplier, status, total, item count, date)
- **Findings**: Risk indicators with emoji badges (⚠️, ❓, ✅)
- **Evidence Table**: Price comparison for each item
  - Item Code | Current Rate | Average Rate | Delta % | Status
- **Recommended Actions**: Specific next steps
  - Negotiate prices
  - Request quotes
  - Confirm delivery dates

## Usage Examples

### Example 1: Simple Approval
```
User: "Should I approve PUR-ORD-2026-00001?"

Response:
Decision: REVIEW
Summary: Supplier: TEST-SUPPLIER | Status: To Receive and Bill | Total: 500 ILS | Items: 1
Findings:
  - Decision: REVIEW (Moderate risks or missing data require review)
  - ❓ Insufficient historical data: 1 item(s) have no past purchase records
  - ℹ️ PO status is 'To Receive and Bill' (not standard for approval)

Evidence Table:
  Item Code | Current Rate | Avg Rate | Delta | Status
  PRINTER   | $500.00      | N/A      | N/A   | ✓

Next Actions:
  → Request quote or market price check for 1 item(s)
```

### Example 2: Price Anomaly Detection
```
User: "Can I approve PUR-ORD-2026-00005?"

Response:
Decision: DO NOT APPROVE
Summary: Supplier: VENDOR-X | Total: 2,500 ILS | Items: 3
Findings:
  - Decision: DO NOT APPROVE (Price anomalies and/or high supplier risk)
  - ⚠️ Price anomalies detected: 2 item(s) >= 20% above average
  - ⚠️ Supplier has 4 open orders pending

Evidence Table:
  Item Code | Current Rate | Avg Rate | Delta   | Status
  CPU       | $450.00      | $375.00  | +20.0%  | 🚨 ANOMALY
  RAM       | $120.00      | $95.00   | +26.3%  | 🚨 ANOMALY
  SSD       | $180.00      | $200.00  | -10.0%  | ✓

Next Actions:
  → Negotiate price on 2 item(s) to match historical average
  → Confirm delivery dates on 4 open orders before approving new orders
```

## Architecture

### New Files
- **app/po_approval_analyzer.py** (233 lines)
  - `analyze_po_approval()` - Main analysis function
  - `calculate_price_anomalies()` - Price comparison logic
  - `get_historical_item_rate()` - Historical data lookup
  - `get_supplier_open_orders()` - Supplier risk check

### Updated Files
- **app/copilot/intent.py** - Added approval intent recognition
- **app/copilot/service.py** - Added approval handler
- **app/templates/copilot.html** - Added approval UI rendering

### Data Flow
```
User Query
    ↓
Intent Parser (detects "approve" keyword + PO name)
    ↓
Service Handler (calls analyze_po_approval)
    ↓
PO Approval Analyzer
  ├── Fetch PO details
  ├── Calculate price anomalies
  ├── Check supplier risk
  ├── Build findings & evidence
  └── Generate decision & actions
    ↓
HTML UI (renders formatted approval response)
```

## Key Metrics

| Metric | Threshold | Impact |
|--------|-----------|--------|
| Price Delta | >= 20% | Flags as ANOMALY |
| Open Orders | >= 3 | Adds 15 points to risk |
| Missing Data | Any | REVIEW decision |
| Anomalies + Risk | >= 30 | DO NOT APPROVE |

## Testing

All tests passing with real ERPNext data:
```bash
# Test 1: Direct module
python -m app.po_approval_analyzer

# Test 2: Service layer
from app.copilot.service import handle_user_input
result = handle_user_input("Should I approve PUR-ORD-2026-00001?")

# Test 3: API endpoint
curl -X POST http://localhost:8001/copilot \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I approve PUR-ORD-2026-00001?"}'
```

## UI Features

- **Color-coded decision badges**:
  - Green for APPROVE ✓
  - Yellow/Orange for REVIEW ⚠️
  - Red for DO NOT APPROVE ✗
- **Price Analysis Table** with sortable columns
- **Action Items** with arrow indicators
- **Summary Panel** with PO metadata
- **Collapsible Sections** for detailed exploration

## Future Enhancements

1. **Supplier History**: Show supplier's past approval patterns
2. **Market Price Comparison**: Compare against industry benchmarks
3. **Delivery Performance**: Factor in supplier's on-time delivery rate
4. **Budget Impact**: Show impact on budget vs. spending plan
5. **Bulk Approval**: Analyze and recommend approval for multiple POs
6. **Approval Workflow**: Route to manager with recommendations
7. **Learning**: Improve thresholds based on approval history

## Integration Points

- **ERPNext API**: Pulls real PO and pricing data
- **Intent Parser**: Recognizes natural approval requests
- **Service Layer**: Orchestrates analysis workflow
- **UI**: Displays formatted recommendations to procurement manager
