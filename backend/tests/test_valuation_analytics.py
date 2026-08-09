from decimal import Decimal

from app.api.valorisation import variation_pct


def test_variation_positive() -> None:
    assert variation_pct(
        Decimal("110"),
        Decimal("100"),
    ) == Decimal("10.0")


def test_variation_negative() -> None:
    assert variation_pct(
        Decimal("90"),
        Decimal("100"),
    ) == Decimal("-10.0")


def test_variation_sans_precedent() -> None:
    assert variation_pct(
        Decimal("100"),
        None,
    ) is None


def test_variation_precedent_zero() -> None:
    assert variation_pct(
        Decimal("100"),
        Decimal("0"),
    ) is None
