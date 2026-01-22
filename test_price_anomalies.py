"""Tests for Price Anomaly Detection"""
import sys
sys.path.insert(0, '.')
from app.price_anomaly_detector import detect_price_anomalies

def test_no_anomalies():
    pos = [{"item_code": "ITEM-001", "supplier": f"S{i}", "rate": 100, "qty": 1} for i in range(3)]
    result = detect_price_anomalies(pos)
    assert result["summary"]["anomaly_count"] == 0
    print("[OK] test_no_anomalies")

def test_one_anomaly():
    pos = [
        {"item_code": "ITEM-001", "supplier": "SA", "rate": 100, "qty": 1},
        {"item_code": "ITEM-001", "supplier": "SB", "rate": 150, "qty": 1},
    ]
    result = detect_price_anomalies(pos)
    assert result["summary"]["anomaly_count"] >= 1
    print("[OK] test_one_anomaly")

def test_empty():
    result = detect_price_anomalies([])
    assert result["summary"]["anomaly_count"] == 0
    print("[OK] test_empty")

def test_critical():
    pos = [
        {"item_code": "ITEM-001", "supplier": "SA", "rate": 100, "qty": 1},
        {"item_code": "ITEM-001", "supplier": "SB", "rate": 200, "qty": 1},
    ]
    result = detect_price_anomalies(pos)
    assert len(result["anomalies"]) > 0
    assert result["anomalies"][0]["severity"] == "Critical"
    print("[OK] test_critical")

def test_formatting():
    pos = [
        {"item_code": "ITEM-001", "supplier": "SA", "rate": 1000.5, "qty": 1},
        {"item_code": "ITEM-001", "supplier": "SB", "rate": 1500.75, "qty": 1},
    ]
    result = detect_price_anomalies(pos)
    assert "$" in result["anomalies"][0]["price"]
    print("[OK] test_formatting")

def test_calc():
    pos = [
        {"item_code": "ITEM-001", "supplier": "SA", "quantity": 10, "amount": 1000},
        {"item_code": "ITEM-001", "supplier": "SB", "quantity": 10, "amount": 1500},
    ]
    result = detect_price_anomalies(pos)
    assert result["summary"]["anomaly_count"] >= 1
    print("[OK] test_calc")

def test_sorting():
    pos = []
    for i in range(3):
        pos.append({"item_code": f"ITEM-{i}", "supplier": "SA", "rate": 100, "qty": 1})
        pos.append({"item_code": f"ITEM-{i}", "supplier": "SB", "rate": 200, "qty": 1})
    result = detect_price_anomalies(pos)
    if len(result["anomalies"]) > 1:
        assert result["anomalies"][0]["percentage_raw"] >= result["anomalies"][-1]["percentage_raw"]
    print("[OK] test_sorting")

def test_rec_limit():
    pos = []
    for i in range(15):
        pos.append({"item_code": f"ITEM-{i}", "supplier": "SA", "rate": 100, "qty": 1})
        pos.append({"item_code": f"ITEM-{i}", "supplier": "SB", "rate": 200, "qty": 1})
    result = detect_price_anomalies(pos)
    assert len(result["recommendations"]) <= 4
    print("[OK] test_rec_limit")

if __name__ == "__main__":
    test_no_anomalies()
    test_one_anomaly()
    test_empty()
    test_critical()
    test_formatting()
    test_calc()
    test_sorting()
    test_rec_limit()
    print("\n==== ALL TESTS PASSED ====")
