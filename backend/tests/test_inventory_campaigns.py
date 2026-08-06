from decimal import Decimal


def calculer_ecart(
    theorique: Decimal,
    comptee: Decimal,
) -> Decimal:
    return comptee - theorique


def test_ecart_positif() -> None:
    assert calculer_ecart(
        Decimal("100"),
        Decimal("105"),
    ) == Decimal("5")


def test_ecart_negatif() -> None:
    assert calculer_ecart(
        Decimal("100"),
        Decimal("96"),
    ) == Decimal("-4")


def test_ecart_nul() -> None:
    assert calculer_ecart(
        Decimal("100"),
        Decimal("100"),
    ) == Decimal("0")
