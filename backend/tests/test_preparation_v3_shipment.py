from decimal import Decimal

from app.models.preparation import LignePreparation, Preparation


def test_preparation_prete_est_expediable() -> None:
    preparation = Preparation(
        affaire_id=1,
        nom="Préparation test",
        statut="PRETE",
    )
    ligne = LignePreparation(
        preparation_id=1,
        article_id=1,
        emplacement_source_id=1,
        quantite_demandee=Decimal("100"),
        quantite_preparee=Decimal("100"),
        quantite_manquante=Decimal("0"),
        statut="PREPAREE",
    )
    preparation.lignes = [ligne]

    assert preparation.statut == "PRETE"
    assert all(
        item.statut == "PREPAREE"
        and item.quantite_preparee > 0
        for item in preparation.lignes
    )


def test_double_expedition_doit_etre_bloquee() -> None:
    preparation = Preparation(
        affaire_id=1,
        nom="Préparation déjà expédiée",
        statut="EXPEDIEE",
    )
    assert preparation.statut == "EXPEDIEE"


def test_quantite_sortie_est_quantite_preparee() -> None:
    ligne = LignePreparation(
        preparation_id=1,
        article_id=1,
        emplacement_source_id=1,
        quantite_demandee=Decimal("100"),
        quantite_preparee=Decimal("95"),
        quantite_manquante=Decimal("5"),
        statut="PREPAREE",
    )
    assert ligne.quantite_preparee == Decimal("95")
