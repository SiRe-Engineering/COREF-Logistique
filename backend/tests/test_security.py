from app.core.security import (
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)


def test_mot_de_passe_valide() -> None:
    valeur = hacher_mot_de_passe("MotDePasse-2026!")
    assert verifier_mot_de_passe("MotDePasse-2026!", valeur)


def test_mot_de_passe_invalide() -> None:
    valeur = hacher_mot_de_passe("MotDePasse-2026!")
    assert not verifier_mot_de_passe("Erreur-2026!", valeur)
