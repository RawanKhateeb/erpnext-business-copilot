# MCP Integration for ERPNext Copilot

This document explains how to use the MCP (Model Context Protocol) interface with your ERPNext Copilot.

## Overview

The MCP server allows LLMs (like Claude, GPT, etc.) to access your ERPNext data through the Model Context Protocol.

**Key Features:**
- ✅ Reuses existing service layer (no code duplication)
- ✅ Independent from REST API (both can run simultaneously)
- ✅ 5 exported tools for ERPNext queries
- ✅ Production-ready with logging and error handling

---

## Architecture

```
LLM (Claude, etc.)
    ↓ (MCP Protocol)
MCP Server (app/mcp_server.py)
    ↓ (function calls)
Existing Service Layer
    ├─ app.copilot.service.handle_user_input()
    ├─ app.erpnext_client.ERPNextClient
    └─ app.erpnext_client methods
    ↓
ERPNext API
```

**No changes to existing code** - MCP is a thin wrapper around existing functions.

---

## Available MCP Tools

### 1. `list_suppliers`
Get all suppliers from ERPNext.

**Parameters:** None

**Example:**
```json
{
  "name": "list_suppliers",
  "arguments": {}
}
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "suppliers": [
    {"name": "TEST-SUPPLIER", "supplier_name": "Test Supplier Co.", ...},
    ...
  ]
}
```

---

### 2. `list_items`
Get all items/products from inventory.

**Parameters:** None

**Example:**
```json
{
  "name": "list_items",
  "arguments": {}
}
```

**Response:**
```json
{
  "success": true,
  "count": 25,
  "items": [
    {"name": "TEST-ITEM", "item_name": "Test Item", ...},
    ...
  ]
}
```

---

### 3. `list_purchase_orders`
Get purchase orders with optional limit.

**Parameters:**
- `limit` (integer, optional): Max results (default: 50)

**Example:**
```json
{
  "name": "list_purchase_orders",
  "arguments": {"limit": 20}
}
```

**Response:**
```json
{
  "success": true,
  "count": 1,
  "limit": 20,
  "purchase_orders": [
    {
      "name": "PUR-ORD-2026-00001",
      "supplier": "TEST-SUPPLIER",
      "transaction_date": "2026-01-21",
      "status": "To Receive and Bill",
      "grand_total": 500,
      ...
    }
  ]
}
```

---

### 4. `get_purchase_order`
Get detailed information about a specific purchase order.

**Parameters:**
- `po_name` (string, required): Purchase order name (e.g., "PUR-ORD-2026-00001")

**Example:**
```json
{
  "name": "get_purchase_order",
  "arguments": {"po_name": "PUR-ORD-2026-00001"}
}
```

**Response:**
```json
{
  "success": true,
  "purchase_order": {
    "name": "PUR-ORD-2026-00001",
    "supplier": "TEST-SUPPLIER",
    "transaction_date": "2026-01-21",
    "status": "To Receive and Bill",
    "grand_total": 500,
    "items": [
      {
        "item_code": "TEST-ITEM",
        "qty": 10,
        "rate": 50,
        "amount": 500,
        ...
      }
    ],
    ...
  }
}
```

---

### 5. `copilot_ask`
Ask the copilot a natural language question about ERPNext data.

Uses intent parsing and service layer to provide intelligent insights.

**Parameters:**
- `query` (string, required): Natural language question
- `limit` (integer, optional): Max results for list queries (default: 20)

**Example Queries:**
- "What suppliers do we have?"
- "Show pending purchase orders"
- "Generate monthly spend report"
- "List items"
- "Show me PUR-ORD-2026-00001"

**Example:**
```json
{
  "name": "copilot_ask",
  "arguments": {
    "query": "What suppliers do we have?",
    "limit": 20
  }
}
```

**Response:**
```json
{
  "success": true,
  "query": "What suppliers do we have?",
  "intent": "list_suppliers",
  "answer": "You have 1 suppliers in your network.",
  "insights": [
    "You work with 1 suppliers.",
    "Consider diversifying your supplier base for better resilience."
  ],
  "data": [...],
  "next_questions": [...]
}
```

---

## Installation & Setup

### 1. Install MCP Library
```bash
pip install -r requirements.txt
# or specifically:
pip install mcp
```

### 2. Start the MCP Server
```bash
# Option A: Direct Python
python run_mcp_server.py

# Option B: Using Python module
python -m app.mcp_server
```

You should see:
```
2026-01-22 10:30:15,123 - app.mcp_server - INFO - Starting ERPNext Copilot MCP Server...
2026-01-22 10:30:15,456 - app.mcp_server - INFO - Available tools: ['list_suppliers', 'list_items', 'list_purchase_orders', 'get_purchase_order', 'copilot_ask']
2026-01-22 10:30:15,789 - app.mcp_server - INFO - MCP Server started and listening for requests...
```

### 3. Configure Claude/LLM to Use MCP Server

**For Claude Desktop:**
Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "erpnext-copilot": {
      "command": "python",
      "args": ["/path/to/your/project/run_mcp_server.py"]
    }
  }
}
```

Then restart Claude Desktop. The ERPNext Copilot tools will be available in Claude.

**For Other LLMs:**
Check their MCP documentation for integration steps.

---

## Running Both REST API and MCP Server

You can run both simultaneously in different terminals:

**Terminal 1 - REST API (FastAPI):**
```bash
cd /path/to/project
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - MCP Server:**
```bash
cd /path/to/project
python run_mcp_server.py
```

Now:
- Web UI works at `http://localhost:8000`
- LLMs can access tools via MCP
- All reusing the same service layer and business logic

---

## Code Structure

```
app/
├── mcp_server.py          # ← NEW: MCP server implementation
├── copilot/
│   ├── service.py         # ← Reused by MCP
│   └── intent.py          # ← Reused by MCP
├── erpnext_client.py      # ← Reused by MCP
├── main.py                # ← REST API (unchanged)
└── templates/
    └── copilot.html       # ← Web UI (unchanged)

run_mcp_server.py          # ← NEW: Startup script
```

**Key Point:** MCP server imports and reuses existing modules. No logic duplication.

---

## Example: Using with Claude

Once configured, Claude can do things like:

**User:** "Give me a summary of my pending purchase orders"

**Claude:** *Uses `copilot_ask` tool with query "pending orders"*
```json
{
  "intent": "pending_report",
  "answer": "You have 3 pending purchase orders...",
  "insights": [...],
  "data": [...]
}
```

**Claude Response:** "Based on your ERPNext data, you have 3 pending purchase orders totaling $5,000. Items to receive: 2 orders. Items to bill: 1 order. I recommend coordinating with your warehouse team..."

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'mcp'"
```bash
pip install mcp
# or
pip install -r requirements.txt
```

### "ERPNextClient failed to initialize"
Check your `.env` file has:
```
ERP_URL=http://your-erp-url
ERP_API_KEY=your-key
ERP_API_SECRET=your-secret
```

### MCP Server crashes silently
Run with stderr visible:
```bash
python run_mcp_server.py 2>&1 | tee mcp.log
```

---

## Performance Notes

- MCP server is lightweight (thin wrapper)
- Reuses connection pooling from ERPNextClient
- Same performance as REST API for data operations
- Good for integrating with LLMs

---

## Security Considerations

1. **Environment Variables:** Keep `.env` secure, don't commit it
2. **API Keys:** Use strong ERPNext API credentials
3. **MCP Transport:** stdio is secure (local only)
4. **Rate Limiting:** Consider adding rate limits if exposing to network

---

## Future Enhancements

Possible additions:
- [ ] Add `create_purchase_order` tool (write operations)
- [ ] Add `export_to_csv` tool
- [ ] Add `schedule_report` tool
- [ ] WebSocket support for real-time updates
- [ ] Multi-tenant support

---

## Support

For issues with:
- **REST API/Web UI:** See main README
- **MCP Server:** Check logs in stderr
- **ERPNext Connection:** Verify `.env` configuration
- **Claude Integration:** See Claude MCP documentation

