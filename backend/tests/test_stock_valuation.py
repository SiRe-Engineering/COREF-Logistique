from decimal import Decimal

from app.services.mouvements import _calculer_cump_entree


def test_cump_sur_premiere_entree() -> None:
    assert _calculer_cump_entree(
        quantite_existante=Decimal("0"),
        cump_existant=Decimal("0"),
        quantite_entree=Decimal("100"),
        prix_entree=Decimal("2.84"),
    ) == Decimal("2.84")


def test_cump_pondere() -> None:
    resultat = _calculer_cump_entree(
        quantite_existante=Decimal("100"),
        cump_existant=Decimal("2"),
        quantite_entree=Decimal("100"),
        prix_entree=Decimal("4"),
    )
    assert resultat == Decimal("3")


def test_valeur_sortie_figee() -> None:
    quantite = Decimal("25")
    cout = Decimal("3.50")
    assert (quantite * cout).quantize(Decimal("0.01")) == Decimal("87.50")
