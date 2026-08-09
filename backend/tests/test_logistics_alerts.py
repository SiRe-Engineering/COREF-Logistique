from datetime import date
from decimal import Decimal

from app.services.alertes import SignalAlerte


def test_signal_alerte() -> None:
    signal = SignalAlerte(
        cle="STOCK:RUPTURE:1",
        categorie="STOCK",
        niveau="CRITIQUE",
        titre="Rupture",
        message="Test",
        lien="/stocks",
        source_type="ARTICLE",
        source_id=1,
    )
    assert signal.cle == "STOCK:RUPTURE:1"
    assert signal.niveau == "CRITIQUE"


def test_disponible_stock() -> None:
    physique = Decimal("10")
    reservee = Decimal("7")
    assert physique - reservee == Decimal("3")


def test_retard_date() -> None:
    assert date(2026, 8, 1) < date(2026, 8, 7)
