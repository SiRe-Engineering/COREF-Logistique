from decimal import Decimal

from app.models.preparation import LignePreparation
from app.schemas.preparation import LignePreparationUpdate


def test_schema_accepte_ligne_partielle() -> None:
    payload = LignePreparationUpdate(
        quantite_preparee=Decimal("4"),
        statut="PARTIELLE",
        motif_ecart="Stock physique incomplet",
    )
    assert payload.statut == "PARTIELLE"
    assert payload.motif_ecart == "Stock physique incomplet"


def test_modele_expose_quantite_manquante() -> None:
    ligne = LignePreparation(
        preparation_id=1,
        article_id=1,
        quantite_demandee=Decimal("10"),
        quantite_preparee=Decimal("4"),
        quantite_manquante=Decimal("6"),
        statut="PARTIELLE",
    )
    assert ligne.quantite_manquante == Decimal("6")
