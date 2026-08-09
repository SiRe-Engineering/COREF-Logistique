from datetime import date,timedelta
def test_expired(): assert date.today()-timedelta(days=1)<date.today()
def test_due_30_days(): assert date.today()+timedelta(days=20)<=date.today()+timedelta(days=30)
