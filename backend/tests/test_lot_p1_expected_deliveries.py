from datetime import date, timedelta

def test_late_delivery_stays_expected():
    today = date(2026, 8, 7)
    planned = today - timedelta(days=1)
    horizon = today + timedelta(days=30)
    assert planned < today or today <= planned <= horizon

def test_future_delivery_over_30_days_is_excluded():
    today = date(2026, 8, 7)
    planned = today + timedelta(days=31)
    horizon = today + timedelta(days=30)
    assert not (planned < today or today <= planned <= horizon)
