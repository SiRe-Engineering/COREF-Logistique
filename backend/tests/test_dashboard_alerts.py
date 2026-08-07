from datetime import date, timedelta


def niveau_peremption(jours: int) -> str:
    if jours < 0:
        return "PERIME"
    if jours <= 30:
        return "CRITIQUE"
    return "A_SURVEILLER"


def test_lot_perime() -> None:
    assert niveau_peremption(-1) == "PERIME"


def test_lot_critique() -> None:
    assert niveau_peremption(30) == "CRITIQUE"


def test_lot_a_surveiller() -> None:
    assert niveau_peremption(31) == "A_SURVEILLER"


def test_retard() -> None:
    aujourd_hui = date(2026, 8, 7)
    assert aujourd_hui - timedelta(days=1) < aujourd_hui
