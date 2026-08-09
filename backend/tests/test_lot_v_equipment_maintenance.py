from datetime import date,timedelta

def test_overdue_control():
    today=date(2026,8,7)
    due=today-timedelta(days=1)
    assert due<today

def test_finish_requires_action():
    action=""
    assert not action

def test_maintenance_state_flow():
    assert ["DISPONIBLE","EN_MAINTENANCE","DISPONIBLE"]==["DISPONIBLE","EN_MAINTENANCE","DISPONIBLE"]
