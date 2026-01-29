"""
Mock data for API tests.
Plain Python variables (no pytest fixtures).
"""

MOCK_SUPPLIERS = [
    {
        "name": "Supplier A",
        "supplier_name": "Supplier A",
        "supplier_group": "Local",
        "country": "USA",
        "disabled": 0,
    },
    {
        "name": "Supplier B",
        "supplier_name": "Supplier B",
        "supplier_group": "International",
        "country": "China",
        "disabled": 0,
    },
    {
        "name": "Supplier C",
        "supplier_name": "Supplier C",
        "supplier_group": "Local",
        "country": "USA",
        "disabled": 0,
    },
]

MOCK_ITEMS = [
    {
        "name": "Item-001",
        "item_code": "Item-001",
        "item_name": "Raw Material A",
        "item_group": "Raw Materials",
        "stock_qty": 100,
        "valuation_rate": 10.5,
    },
    {
        "name": "Item-002",
        "item_code": "Item-002",
        "item_name": "Component B",
        "item_group": "Components",
        "stock_qty": 250,
        "valuation_rate": 25.0,
    },
]

MOCK_PURCHASE_ORDERS = [
    {
        "name": "PO-2024-001",
        "supplier": "Supplier A",
        "supplier_name": "Supplier A",
        "grand_total": 5000.00,
        "status": "Completed",
        "transaction_date": "2024-01-15",
        "delivery_date": "2024-01-20",
    },
    {
        "name": "PO-2024-002",
        "supplier": "Supplier B",
        "supplier_name": "Supplier B",
        "grand_total": 7500.00,
        "status": "Submitted",
        "transaction_date": "2024-02-10",
        "delivery_date": "2024-02-20",
    },
    {
        "name": "PO-2024-003",
        "supplier": "Supplier A",
        "supplier_name": "Supplier A",
        "grand_total": 3200.00,
        "status": "Draft",
        "transaction_date": "2024-02-15",
        "delivery_date": "2024-02-25",
    },
]

MOCK_PURCHASE_ORDER_DETAIL = {
    "name": "PO-2024-001",
    "doctype": "Purchase Order",
    "supplier": "Supplier A",
    "supplier_name": "Supplier A",
    "grand_total": 5000.00,
    "status": "Completed",
    "transaction_date": "2024-01-15",
    "delivery_date": "2024-01-20",
    "items": [
        {
            "item_code": "Item-001",
            "qty": 50,
            "rate": 100.0,
            "amount": 5000.0,
        }
    ],
}

MOCK_AI_REPORT = {
    "report": "Monthly procurement analysis shows stable supplier performance.",
    "summary": "Cost-effective purchasing with competitive rates.",
}

MOCK_ERROR_RESPONSE = {
    "detail": "Internal server error"
}
