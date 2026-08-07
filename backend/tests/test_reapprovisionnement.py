from decimal import Decimal

from app.services.reapprovisionnement import quantite_suggeree


def test_suggestion_avec_stock_maximum() -> None:
    assert quantite_suggeree(
        disponible=Decimal("420"),
        minimum=Decimal("500"),
        maximum=Decimal("1500"),
    ) == Decimal("1080")


def test_suggestion_sans_stock_maximum() -> None:
    assert quantite_suggeree(
        disponible=Decimal("120"),
        minimum=Decimal("500"),
        maximum=Decimal("0"),
    ) == Decimal("380")
