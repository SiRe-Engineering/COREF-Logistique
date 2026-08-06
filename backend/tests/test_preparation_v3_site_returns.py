from decimal import Decimal


def quantite_retournable(
    expediee: Decimal,
    retournee: Decimal,
) -> Decimal:
    return max(expediee - retournee, Decimal("0"))


def test_retour_partiel() -> None:
    assert quantite_retournable(
        Decimal("100"),
        Decimal("35"),
    ) == Decimal("65")


def test_retour_total() -> None:
    assert quantite_retournable(
        Decimal("100"),
        Decimal("100"),
    ) == Decimal("0")


def test_retour_superieur_expedition_refuse() -> None:
    expediee = Decimal("100")
    deja_retournee = Decimal("20")
    nouveau_retour = Decimal("90")

    assert nouveau_retour > quantite_retournable(
        expediee,
        deja_retournee,
    )
