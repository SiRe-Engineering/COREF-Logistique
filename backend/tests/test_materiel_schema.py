from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.materiel import MaterielCreate


def test_materiel_disponible_valide() -> None:
    materiel = MaterielCreate(
        designation="Malaxeur 50 L",
        categorie="Malaxeur",
    )
    assert materiel.etat == "DISPONIBLE"


def test_materiel_en_chantier_sans_affaire_refuse() -> None:
    with pytest.raises(ValidationError):
        MaterielCreate(
            designation="Scie à briques",
            categorie="Scie à briques",
            etat="EN_CHANTIER",
        )


def test_dates_controle_incoherentes_refusees() -> None:
    with pytest.raises(ValidationError):
        MaterielCreate(
            designation="Élingue",
            categorie="Levage",
            date_dernier_controle=date(2026, 8, 10),
            date_prochain_controle=date(2026, 8, 1),
        )
