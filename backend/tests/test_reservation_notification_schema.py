from decimal import Decimal

from app.schemas.stock import StockSet


def test_stock_set_ne_contient_plus_reservation() -> None:
    payload = StockSet(
        article_id=1,
        emplacement_id=2,
        quantite_physique=Decimal("100"),
    )
    assert not hasattr(payload, "quantite_reservee")
