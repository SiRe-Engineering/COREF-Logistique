from decimal import Decimal

from app.models.preparation import RemplacementPreparation


def test_historique_remplacement() -> None:
    remplacement = RemplacementPreparation(
        ligne_preparation_id=1,
        article_origine_id=1,
        article_remplacement_id=2,
        emplacement_remplacement_id=1,
        quantite=Decimal("100"),
        actif=True,
    )
    assert remplacement.article_origine_id == 1
    assert remplacement.article_remplacement_id == 2
    assert remplacement.actif is True
