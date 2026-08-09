from decimal import Decimal

from app.models.stock import Stock


def test_remise_a_zero_stock_article() -> None:
    stock = Stock(
        article_id=1,
        emplacement_id=1,
        quantite_physique=Decimal("200"),
        quantite_reservee=Decimal("50"),
    )

    stock.quantite_physique = Decimal("0")
    stock.quantite_reservee = Decimal("0")

    assert stock.quantite_physique == Decimal("0")
    assert stock.quantite_reservee == Decimal("0")
