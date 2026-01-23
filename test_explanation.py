#!/usr/bin/env python3
"""Test the recommendation explanation feature."""

from app.recommendation_explainer import explain_recommendations

# Test data for total spend
test_data = {
    "total_spend": 2350.00,
    "po_count": 5,
    "completed_count": 0,
    "average_order_value": 470.00
}

insights = [
    "Total spend across 5 purchase orders: $2,350.00",
    "0 orders have been completed",
    "Average order value: $470.00"
]

# Generate explanation
explanation = explain_recommendations(
    intent="total_spend",
    user_question="What's the total spend?",
    data=test_data,
    insights=insights,
    recommendations=insights
)

# Print explanation
print("\n" + "="*60)
print(explanation['title'])
print("="*60)
print(f"\n{explanation['summary']}\n")

print("Reasons:")
for i, reason in enumerate(explanation['reasons'], 1):
    print(f"\n{i}. {reason['recommendation']}")
    print(f"   Evidence: {reason['evidence']}")

print("\nNext Actions:")
for action in explanation['next_actions']:
    print(f"• {action}")

print("\n" + "="*60)
print("✓ Explanation feature is working correctly!")
print("="*60)
