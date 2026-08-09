from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.affaire import AffaireCreate
from app.schemas.mouvement import MouvementCreate


def test_affaire_valide() -> None:
    affaire = AffaireCreate(
        code_externe="A26-145",
        nom="Réfection chaudière",
        date_debut=date(2026, 8, 10),
        date_fin_prevue=date(2026, 8, 20),
    )
    assert affaire.code_externe == "A26-145"


def test_dates_affaire_incoherentes_refusees() -> None:
    with pytest.raises(ValidationError):
        AffaireCreate(
            nom="Chantier test",
            date_debut=date(2026, 8, 20),
            date_fin_prevue=date(2026, 8, 10),
        )


def test_sortie_sans_affaire_ni_sortie_libre_refusee() -> None:
    with pytest.raises(ValidationError):
        MouvementCreate(
            type="SORTIE",
            article_id=1,
            emplacement_source_id=1,
            quantite=10,
        )


def test_sortie_libre_acceptee() -> None:
    mouvement = MouvementCreate(
        type="SORTIE",
        article_id=1,
        emplacement_source_id=1,
        quantite=10,
        sortie_libre=True,
    )
    assert mouvement.sortie_libre is True
