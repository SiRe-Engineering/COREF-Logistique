from decimal import Decimal

from app.schemas.preparation import LignePreparationCreate


def test_ligne_preparation_valide() -> None:
    ligne = LignePreparationCreate(
        article_id=1,
        emplacement_source_id=2,
        quantite_demandee=Decimal("25"),
    )
    assert ligne.quantite_demandee == Decimal("25")
