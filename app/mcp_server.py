"""
MCP (Model Context Protocol) Server for ERPNext Copilot

This module provides an MCP interface to the ERPNext Copilot skill.
It wraps existing service functions and exposes them as MCP tools.

LLMs can call these tools via MCP protocol to:
- Query suppliers, items, and purchase orders
- Get details on specific purchase orders
- Ask natural language questions about ERP data

Architecture:
- Reuses: app.copilot.service.handle_user_input()
- Reuses: app.erpnext_client.ERPNextClient
- No business logic duplication
- Standalone MCP server (independent of REST API)
"""

import json
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import existing service layer
from app.copilot.service import handle_user_input
from app.erpnext_client import ERPNextClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = Server("erpnext-copilot")

# Initialize client
client = ERPNextClient()


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

TOOLS = [
    Tool(
        name="list_suppliers",
        description="Get a list of all suppliers from ERPNext",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="list_items",
        description="Get a list of all items/products from ERPNext inventory",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="list_purchase_orders",
        description="Get a list of purchase orders with limit",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of purchase orders to return (default: 50)",
                }
            },
            "required": [],
        },
    ),
    Tool(
        name="get_purchase_order",
        description="Get detailed information about a specific purchase order",
        inputSchema={
            "type": "object",
            "properties": {
                "po_name": {
                    "type": "string",
                    "description": "Purchase order name/ID (e.g., PUR-ORD-2026-00001)",
                }
            },
            "required": ["po_name"],
        },
    ),
    Tool(
        name="copilot_ask",
        description="Ask the Copilot a natural language question about ERPNext data. The copilot will parse intent and return insights.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question (e.g., 'What suppliers do we have?', 'Show pending orders', 'Generate monthly report')",
                },
                "limit": {
                    "type": "integer",
                    "description": "Optional limit for list results (default: 20)",
                },
            },
            "required": ["query"],
        },
    ),
]


# ============================================================================
# HANDLER FUNCTIONS (wrap existing service logic)
# ============================================================================


def handle_list_suppliers() -> Dict[str, Any]:
    """List all suppliers - wraps client.list_suppliers()"""
    try:
        suppliers = client.list_suppliers()
        return {
            "success": True,
            "count": len(suppliers) if suppliers else 0,
            "suppliers": suppliers or [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch suppliers from ERPNext",
        }


def handle_list_items() -> Dict[str, Any]:
    """List all items - wraps client.list_items()"""
    try:
        items = client.list_items()
        return {
            "success": True,
            "count": len(items) if items else 0,
            "items": items or [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch items from ERPNext",
        }


def handle_list_purchase_orders(limit: int = 50) -> Dict[str, Any]:
    """List purchase orders - wraps client.list_purchase_orders()"""
    try:
        pos = client.list_purchase_orders(limit=limit)
        return {
            "success": True,
            "count": len(pos) if pos else 0,
            "limit": limit,
            "purchase_orders": pos or [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch purchase orders from ERPNext",
        }


def handle_get_purchase_order(po_name: str) -> Dict[str, Any]:
    """Get PO details - wraps client.get_purchase_order()"""
    try:
        po = client.get_purchase_order(po_name)
        return {
            "success": True,
            "purchase_order": po,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch purchase order {po_name}",
        }


def handle_copilot_ask(query: str, limit: int = 20) -> Dict[str, Any]:
    """Ask copilot - wraps handle_user_input() from service layer"""
    try:
        response = handle_user_input(query)
        return {
            "success": True,
            "query": query,
            **response,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process copilot query",
        }


# ============================================================================
# MCP TOOL REGISTRATION
# ============================================================================


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available MCP tools"""
    return TOOLS


@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle MCP tool calls from LLM.
    Routes to appropriate handler and returns results.
    """
    logger.info(f"MCP tool called: {name} with args: {arguments}")

    try:
        result = None

        if name == "list_suppliers":
            result = handle_list_suppliers()

        elif name == "list_items":
            result = handle_list_items()

        elif name == "list_purchase_orders":
            limit = arguments.get("limit", 50)
            result = handle_list_purchase_orders(limit)

        elif name == "get_purchase_order":
            po_name = arguments.get("po_name")
            if not po_name:
                result = {"success": False, "error": "po_name parameter is required"}
            else:
                result = handle_get_purchase_order(po_name)

        elif name == "copilot_ask":
            query = arguments.get("query")
            if not query:
                result = {"success": False, "error": "query parameter is required"}
            else:
                limit = arguments.get("limit", 20)
                result = handle_copilot_ask(query, limit)

        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}

        # Return as JSON TextContent
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "message": f"Error executing tool {name}",
                }),
            )
        ]


# ============================================================================
# SERVER STARTUP
# ============================================================================


async def main():
    """
    Start the MCP server.
    
    Usage:
        python run_mcp_server.py
    
    The server will listen on stdio and process incoming MCP requests.
    """
    logger.info("Starting ERPNext Copilot MCP Server...")
    logger.info(f"Available tools: {[tool.name for tool in TOOLS]}")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server started and listening on stdio...")
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
