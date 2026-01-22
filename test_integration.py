#!/usr/bin/env python
"""
Integration test for ERPNext Copilot REST API and MCP Server.

This script tests both the FastAPI REST endpoints and MCP server without
needing to run them as background processes.

Usage:
    python test_integration.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules import successfully."""
    print("=" * 60)
    print("TEST 1: Component Imports")
    print("=" * 60)

    try:
        from app.main import app
        print("[OK] FastAPI app imports OK")
    except Exception as e:
        print(f"[FAIL] FastAPI app import failed: {e}")
        return False

    try:
        from app.mcp_server import mcp, TOOLS
        print(f"[OK] MCP server imports OK")
        print(f"  Tools available: {[t.name for t in TOOLS]}")
    except Exception as e:
        print(f"[FAIL] MCP server import failed: {e}")
        return False

    try:
        from app.copilot.service import handle_user_input
        print("[OK] Service layer imports OK")
    except Exception as e:
        print(f"[FAIL] Service layer import failed: {e}")
        return False

    try:
        from app.copilot.intent import parse_intent
        print("[OK] Intent parser imports OK")
    except Exception as e:
        print(f"[FAIL] Intent parser import failed: {e}")
        return False

    try:
        from app.erpnext_client import ERPNextClient
        print("[OK] ERPNext client imports OK")
    except Exception as e:
        print(f"[FAIL] ERPNext client import failed: {e}")
        return False

    print("\n[PASS] All imports successful!\n")
    return True


def test_intent_parser():
    """Test intent parsing functionality."""
    print("=" * 60)
    print("TEST 2: Intent Parser")
    print("=" * 60)

    from app.copilot.intent import parse_intent

    test_cases = [
        ("What suppliers do we have?", "list_suppliers"),
        ("Show items", "list_items"),
        ("List purchase orders", "list_purchase_orders"),
        ("Show me PUR-ORD-2026-00001", "get_purchase_order"),
        ("Generate monthly spend report", "monthly_report"),
        ("What about pending orders?", "pending_report"),
    ]

    all_passed = True
    for query, expected_intent in test_cases:
        result = parse_intent(query)
        intent = result.get("intent")
        status = "[OK]" if intent == expected_intent else "[FAIL]"
        print(f"{status} '{query}' -> {intent}")
        if intent != expected_intent:
            all_passed = False

    print()
    return all_passed


def test_mcp_tools():
    """Test MCP tool definitions."""
    print("=" * 60)
    print("TEST 3: MCP Tool Definitions")
    print("=" * 60)

    from app.mcp_server import TOOLS

    expected_tools = [
        "list_suppliers",
        "list_items",
        "list_purchase_orders",
        "get_purchase_order",
        "copilot_ask",
    ]

    tool_names = [t.name for t in TOOLS]
    all_present = all(t in tool_names for t in expected_tools)

    for tool in TOOLS:
        has_schema = hasattr(tool, "inputSchema") and tool.inputSchema is not None
        status = "[OK]" if has_schema else "[FAIL]"
        print(f"{status} {tool.name:25} - {tool.description[:40]}...")

    print()
    if all_present:
        print("[PASS] All required tools present!\n")
        return True
    else:
        print("[FAIL] Some tools missing!\n")
        return False


def test_fastapi_app():
    """Test FastAPI app structure."""
    print("=" * 60)
    print("TEST 4: FastAPI Routes")
    print("=" * 60)

    from app.main import app

    routes = {
        route.path: route.methods
        for route in app.routes
        if hasattr(route, "methods")
    }

    expected_paths = ["/", "/health", "/suppliers", "/items", "/purchase-orders", "/copilot", "/copilot/ask"]

    for path in expected_paths:
        if path in routes:
            methods = ", ".join(routes[path])
            print(f"[OK] {path:25} {methods}")
        else:
            print(f"[FAIL] {path:25} NOT FOUND")

    print()
    return True


def test_handlers():
    """Test MCP handlers can be imported."""
    print("=" * 60)
    print("TEST 5: MCP Handlers")
    print("=" * 60)

    from app.mcp_server import (
        handle_list_suppliers,
        handle_list_items,
        handle_list_purchase_orders,
        handle_get_purchase_order,
        handle_copilot_ask,
    )

    handlers = [
        ("handle_list_suppliers", handle_list_suppliers),
        ("handle_list_items", handle_list_items),
        ("handle_list_purchase_orders", handle_list_purchase_orders),
        ("handle_get_purchase_order", handle_get_purchase_order),
        ("handle_copilot_ask", handle_copilot_ask),
    ]

    for name, handler in handlers:
        is_callable = callable(handler)
        status = "[OK]" if is_callable else "[FAIL]"
        print(f"{status} {name}")

    print()
    return True


def main():
    """Run all tests."""
    print("\n")
    print("=" * 60)
    print("  ERPNext Copilot - Integration Test Suite              ")
    print("=" * 60)
    print()

    tests = [
        ("Component Imports", test_imports),
        ("Intent Parser", test_intent_parser),
        ("MCP Tools", test_mcp_tools),
        ("FastAPI Routes", test_fastapi_app),
        ("MCP Handlers", test_handlers),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}\n")
            results.append((test_name, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for test_name, passed_test in results:
        status = "[OK]" if passed_test else "[FAIL]"
        print(f"{status} {test_name}")

    print()
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n[PASS] ALL TESTS PASSED - System is ready!\n")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
