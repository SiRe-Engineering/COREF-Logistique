import pytest
from pydantic import ValidationError

from app.schemas.mouvement import MouvementCreate


def test_entree_valide() -> None:
    mouvement = MouvementCreate(
        type="ENTREE",
        article_id=1,
        emplacement_destination_id=2,
        quantite=10,
    )
    assert mouvement.type == "ENTREE"


def test_transfert_meme_emplacement_refuse() -> None:
    with pytest.raises(ValidationError):
        MouvementCreate(
            type="TRANSFERT",
            article_id=1,
            emplacement_source_id=2,
            emplacement_destination_id=2,
            quantite=10,
        )


def test_sortie_sans_source_refusee() -> None:
    with pytest.raises(ValidationError):
        MouvementCreate(
            type="SORTIE",
            article_id=1,
            quantite=10,
        )
