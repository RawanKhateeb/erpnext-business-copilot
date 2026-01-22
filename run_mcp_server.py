#!/usr/bin/env python
"""
MCP Server Startup Script for ERPNext Copilot

This script starts the MCP server independently from the REST API.
You can run both the REST API (FastAPI) and MCP server simultaneously.

Usage:
    python run_mcp_server.py

The MCP server will:
- Listen on stdio for MCP protocol messages
- Expose 5 tools: list_suppliers, list_items, list_purchase_orders, get_purchase_order, copilot_ask
- Reuse existing service layer (no code duplication)
- Connect to ERPNext via existing ERPNextClient

Integration with Claude/LLMs:
    Add to your .env or Claude config:
    
    {
      "mcpServers": {
        "erpnext-copilot": {
          "command": "python",
          "args": ["run_mcp_server.py"]
        }
      }
    }
"""

import sys
import logging

# Setup logging to stderr (stdout is used for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Initializing ERPNext Copilot MCP Server...")
        
        # Import here to catch any initialization errors
        from app.mcp_server import main
        import asyncio
        
        logger.info("Starting MCP server...")
        asyncio.run(main())
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        sys.exit(1)
