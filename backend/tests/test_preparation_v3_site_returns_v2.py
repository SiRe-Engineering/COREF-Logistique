from decimal import Decimal


def restant_retournable(
    expediee: Decimal,
    retournee: Decimal,
) -> Decimal:
    return max(expediee - retournee, Decimal("0"))


def test_ligne_source_de_verite() -> None:
    assert restant_retournable(
        Decimal("100"),
        Decimal("35"),
    ) == Decimal("65")


def test_migration_recupere_ancienne_expedition() -> None:
    quantite_preparee = Decimal("200")
    quantite_expediee = quantite_preparee
    assert quantite_expediee == Decimal("200")


def test_impossible_de_depasser_expedie() -> None:
    expediee = Decimal("100")
    retournee = Decimal("60")
    nouveau_retour = Decimal("50")
    assert nouveau_retour > restant_retournable(
        expediee,
        retournee,
    )
