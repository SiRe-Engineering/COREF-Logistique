from decimal import Decimal

def test_purchase_amount_math():
    assert Decimal("10") * Decimal("8.29") == Decimal("82.90")
