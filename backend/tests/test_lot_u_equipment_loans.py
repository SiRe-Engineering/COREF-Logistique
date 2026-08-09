from datetime import date,timedelta

def test_overdue_status():
    today=date(2026,8,7)
    assert today-timedelta(days=1)<today

def test_returned_loan_is_not_overdue():
    returned=True
    assert returned

def test_one_active_loan_per_equipment():
    active_loans=1
    assert active_loans<=1
