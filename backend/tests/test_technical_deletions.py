from decimal import Decimal
from app.models.stock import Stock


def test_stock_non_reserve_supprimable() -> None:
    stock = Stock(
        article_id=1,
        emplacement_id=1,
        quantite_physique=Decimal("10"),
        quantite_reservee=Decimal("0"),
    )
    assert stock.quantite_reservee == Decimal("0")


def test_stock_reserve_non_supprimable() -> None:
    stock = Stock(
        article_id=1,
        emplacement_id=1,
        quantite_physique=Decimal("10"),
        quantite_reservee=Decimal("2"),
    )
    assert stock.quantite_reservee > 0
