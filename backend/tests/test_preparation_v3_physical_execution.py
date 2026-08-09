from decimal import Decimal

from app.models.preparation import LignePreparation


def test_ligne_complete() -> None:
    ligne = LignePreparation(
        preparation_id=1,
        article_id=1,
        quantite_demandee=Decimal("100"),
        quantite_preparee=Decimal("100"),
        quantite_manquante=Decimal("0"),
        statut="PREPAREE",
    )
    assert ligne.quantite_manquante == Decimal("0")


def test_ligne_partielle() -> None:
    ligne = LignePreparation(
        preparation_id=1,
        article_id=1,
        quantite_demandee=Decimal("100"),
        quantite_preparee=Decimal("35"),
        quantite_manquante=Decimal("65"),
        statut="PARTIELLE",
    )
    assert ligne.quantite_manquante == Decimal("65")
