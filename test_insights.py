"""
Tests for the Business Insights Layer

Tests the build_purchase_order_insights() function with various scenarios.
"""

import sys
sys.path.insert(0, '.')

from app.insights import (
    build_purchase_order_insights,
    format_currency,
    format_percentage,
)


def test_format_currency():
    """Test currency formatting."""
    print("Testing format_currency()...")
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(1000000) == "$1,000,000.00"
    assert format_currency(0) == "$0.00"
    assert format_currency(None) == "$0.00"
    assert format_currency("invalid") == "$0.00"
    print("  [OK] Currency formatting works\n")


def test_format_percentage():
    """Test percentage formatting."""
    print("Testing format_percentage()...")
    assert format_percentage(50, 100) == "50.0%"
    assert format_percentage(1, 3) == "33.3%"
    assert format_percentage(0, 100) == "0.0%"
    assert format_percentage(10, 0) == "0.0%"  # Avoid division by zero
    print("  [OK] Percentage formatting works\n")


def test_empty_purchase_orders():
    """Test with empty purchase order list."""
    print("Testing with empty purchase orders...")
    result = build_purchase_order_insights([])
    
    assert result["total_orders"] == 0
    assert result["total_spend"] == 0.0
    assert result["pending_orders_count"] == 0
    assert result["supplier_count"] == 0
    assert len(result["recommendations"]) > 0
    print("  [OK] Empty list handled correctly\n")


def test_single_purchase_order():
    """Test with single purchase order."""
    print("Testing with single purchase order...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "ABC Corp"}
    ]
    result = build_purchase_order_insights(pos)
    
    assert result["total_orders"] == 1
    assert result["total_spend"] == 1000.0
    assert result["total_spend_formatted"] == "$1,000.00"
    assert result["pending_orders_count"] == 0
    assert result["supplier_count"] == 1
    assert result["average_order_value"] == 1000.0
    assert len(result["top_suppliers_by_spend"]) == 1
    print("  [OK] Single order handled correctly\n")


def test_multiple_orders_multiple_suppliers():
    """Test with multiple orders from multiple suppliers."""
    print("Testing with multiple orders and suppliers...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "Supplier A"},
        {"grand_total": 2000, "status": "Completed", "supplier": "Supplier B"},
        {"grand_total": 1500, "status": "To Receive", "supplier": "Supplier A"},
        {"grand_total": 500, "status": "To Bill", "supplier": "Supplier C"},
    ]
    result = build_purchase_order_insights(pos)
    
    assert result["total_orders"] == 4
    assert result["total_spend"] == 5000.0
    assert result["total_spend_formatted"] == "$5,000.00"
    assert result["pending_orders_count"] == 2  # To Receive and To Bill
    assert result["supplier_count"] == 3
    assert result["average_order_value"] == 1250.0
    
    # Check top suppliers
    top_suppliers = result["top_suppliers_by_spend"]
    assert len(top_suppliers) <= 3
    assert top_suppliers[0]["name"] == "Supplier A"
    assert top_suppliers[0]["spend"] == 2500.0
    
    print("  [OK] Multiple orders handled correctly\n")


def test_status_counting():
    """Test status breakdown counting."""
    print("Testing status counting...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "A"},
        {"grand_total": 500, "status": "Completed", "supplier": "A"},
        {"grand_total": 200, "status": "To Receive and Bill", "supplier": "B"},
        {"grand_total": 300, "status": "To Bill", "supplier": "B"},
    ]
    result = build_purchase_order_insights(pos)
    
    counts = result["counts_by_status"]
    assert counts["Completed"] == 2
    assert counts["To Receive and Bill"] == 1
    assert counts["To Bill"] == 1
    print("  [OK] Status counting works\n")


def test_recommendations_pending_orders():
    """Test recommendations for pending orders."""
    print("Testing recommendations for pending orders...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "A"},
        {"grand_total": 500, "status": "To Receive", "supplier": "A"},
        {"grand_total": 300, "status": "To Bill", "supplier": "B"},
        {"grand_total": 200, "status": "To Receive", "supplier": "B"},
    ]
    result = build_purchase_order_insights(pos)
    
    recommendations = result["recommendations"]
    assert len(recommendations) > 0
    # Should mention pending orders
    assert any("pending" in rec.lower() for rec in recommendations)
    print("  [OK] Pending orders recommendations generated\n")


def test_recommendations_supplier_concentration():
    """Test recommendations for high supplier concentration."""
    print("Testing recommendations for supplier concentration...")
    pos = [
        {"grand_total": 4500, "status": "Completed", "supplier": "Dominant Corp"},
        {"grand_total": 500, "status": "Completed", "supplier": "Small Supplier"},
    ]
    result = build_purchase_order_insights(pos)
    
    recommendations = result["recommendations"]
    # Should mention concentration
    assert any("diversify" in rec.lower() for rec in recommendations)
    print("  [OK] Supplier concentration recommendations generated\n")


def test_recommendations_few_suppliers():
    """Test recommendations for too few suppliers."""
    print("Testing recommendations for few suppliers...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "A"},
        {"grand_total": 1000, "status": "Completed", "supplier": "B"},
    ]
    result = build_purchase_order_insights(pos)
    
    recommendations = result["recommendations"]
    # Should mention supplier diversification
    assert any("diversify" in rec.lower() for rec in recommendations)
    print("  [OK] Few suppliers recommendations generated\n")


def test_missing_grand_total():
    """Test handling of missing grand_total."""
    print("Testing handling of missing grand_total...")
    pos = [
        {"status": "Completed", "supplier": "A"},  # Missing grand_total
        {"grand_total": None, "status": "Completed", "supplier": "B"},
        {"grand_total": 1000, "status": "Completed", "supplier": "C"},
    ]
    result = build_purchase_order_insights(pos)
    
    # Should handle gracefully, treating missing as 0
    assert result["total_spend"] == 1000.0
    assert result["total_orders"] == 3
    print("  [OK] Missing grand_total handled safely\n")


def test_top_suppliers_limit():
    """Test that top suppliers are limited to 3."""
    print("Testing top suppliers limit...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "A"},
        {"grand_total": 2000, "status": "Completed", "supplier": "B"},
        {"grand_total": 3000, "status": "Completed", "supplier": "C"},
        {"grand_total": 4000, "status": "Completed", "supplier": "D"},
        {"grand_total": 5000, "status": "Completed", "supplier": "E"},
    ]
    result = build_purchase_order_insights(pos)
    
    # Should only have top 3
    assert len(result["top_suppliers_by_spend"]) == 3
    top_names = [s["name"] for s in result["top_suppliers_by_spend"]]
    assert "E" in top_names  # Highest spend
    assert "D" in top_names  # 2nd highest
    assert "C" in top_names  # 3rd highest
    print("  [OK] Top suppliers limited to 3\n")


def test_output_structure():
    """Test that output has all required fields."""
    print("Testing output structure...")
    pos = [
        {"grand_total": 1000, "status": "Completed", "supplier": "A"}
    ]
    result = build_purchase_order_insights(pos)
    
    required_fields = [
        "total_orders",
        "total_spend",
        "total_spend_formatted",
        "counts_by_status",
        "top_suppliers_by_spend",
        "pending_orders_count",
        "supplier_count",
        "average_order_value",
        "average_order_value_formatted",
        "recommendations",
    ]
    
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    print("  [OK] All required fields present\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BUSINESS INSIGHTS LAYER - TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        test_format_currency,
        test_format_percentage,
        test_empty_purchase_orders,
        test_single_purchase_order,
        test_multiple_orders_multiple_suppliers,
        test_status_counting,
        test_recommendations_pending_orders,
        test_recommendations_supplier_concentration,
        test_recommendations_few_suppliers,
        test_missing_grand_total,
        test_top_suppliers_limit,
        test_output_structure,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  [FAIL] ERROR: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    if failed == 0:
        print("[PASS] ALL TESTS PASSED!\n")
        return 0
    else:
        print(f"[FAIL] {failed} test(s) failed\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
