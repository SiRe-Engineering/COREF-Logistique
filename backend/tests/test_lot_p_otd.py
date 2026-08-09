from datetime import date,datetime,timezone
from decimal import Decimal
def test_otd_on_time():
    planned=date(2026,8,7);received=datetime(2026,8,7,15,tzinfo=timezone.utc)
    assert max(0,(received.date()-planned).days)==0
def test_otd_late():
    planned=date(2026,8,7);received=datetime(2026,8,10,8,tzinfo=timezone.utc)
    assert max(0,(received.date()-planned).days)==3
def test_quantity_variance():
    assert Decimal("9")-Decimal("10")==Decimal("-1")
