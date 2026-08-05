import pytest
from pydantic import ValidationError

from app.schemas.stock import StockSet


def test_stock_valide() -> None:
    stock = StockSet(
        article_id=1,
        emplacement_id=1,
        quantite_physique=100,
        quantite_reservee=20,
    )
    assert stock.quantite_physique == 100
    assert stock.quantite_reservee == 20


def test_reserve_superieure_au_physique_refusee() -> None:
    with pytest.raises(ValidationError):
        StockSet(
            article_id=1,
            emplacement_id=1,
            quantite_physique=10,
            quantite_reservee=12,
        )
