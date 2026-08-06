from decimal import Decimal

from app.schemas.stock import StockSet


def test_stock_beton_accepte_un_lot() -> None:
    payload = StockSet(
        article_id=1,
        lot_id=2,
        emplacement_id=3,
        quantite_physique=Decimal("200"),
    )
    assert payload.lot_id == 2


def test_stock_classique_accepte_lot_absent() -> None:
    payload = StockSet(
        article_id=1,
        lot_id=None,
        emplacement_id=3,
        quantite_physique=Decimal("50"),
    )
    assert payload.lot_id is None
