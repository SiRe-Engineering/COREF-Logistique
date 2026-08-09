import pytest
from pydantic import ValidationError

from app.schemas.utilisateur import UtilisateurCreate


def test_compte_metier_exige_prenom_et_nom() -> None:
    with pytest.raises(ValidationError):
        UtilisateurCreate(
            email="test@coref.fr",
            mot_de_passe="MotDePasse-2026!",
            role="UTILISATEUR_STANDARD",
            type_compte="METIER",
            entreprise="COREF",
        )


def test_compte_technique_accepte_nom_affiche() -> None:
    compte = UtilisateurCreate(
        nom_complet="SiRe Engineering",
        email="support@sire-engineering.fr",
        mot_de_passe="MotDePasse-2026!",
        role="ADMINISTRATEUR_TECHNIQUE",
        type_compte="TECHNIQUE",
        entreprise="SiRe Engineering",
    )
    assert compte.nom_complet == "SiRe Engineering"
