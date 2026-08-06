from decimal import Decimal

from app.schemas.preparation import (
    DecisionRemplacementCreate,
    PropositionRemplacementCreate,
)


def test_proposition_remplacement_valide() -> None:
    payload = PropositionRemplacementCreate(
        article_remplacement_id=2,
        lot_remplacement_id=None,
        emplacement_remplacement_id=1,
        quantite_remplacement=Decimal("10"),
        commentaire_remplacement="Alternative proposée par le magasin.",
    )
    assert payload.quantite_remplacement == Decimal("10")


def test_decision_remplacement_accepte_commentaire_vide() -> None:
    payload = DecisionRemplacementCreate(commentaire_decision=None)
    assert payload.commentaire_decision is None
