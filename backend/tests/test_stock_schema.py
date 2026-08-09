from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.stock import StockSet


def test_stock_valide() -> None:
    stock = StockSet(
        article_id=1,
        emplacement_id=1,
        quantite_physique=Decimal("100"),
    )

    assert stock.article_id == 1
    assert stock.emplacement_id == 1
    assert stock.quantite_physique == Decimal("100")
    assert not hasattr(stock, "quantite_reservee")


def test_quantite_physique_negative_refusee() -> None:
    with pytest.raises(ValidationError):
        StockSet(
            article_id=1,
            emplacement_id=1,
            quantite_physique=Decimal("-1"),
        )
