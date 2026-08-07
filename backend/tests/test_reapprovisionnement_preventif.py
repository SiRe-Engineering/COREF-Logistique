from decimal import Decimal
from app.services.reapprovisionnement import quantite_suggeree

def test_avec_maximum_remonte_au_maximum():
    assert quantite_suggeree(
        disponible=Decimal("10"), minimum=Decimal("10"),
        maximum=Decimal("20"), seuil_alerte=Decimal("10")
    ) == Decimal("10")

def test_au_seuil_sans_maximum_reste_visible():
    assert quantite_suggeree(
        disponible=Decimal("10"), minimum=Decimal("10"),
        maximum=Decimal("0"), seuil_alerte=Decimal("10")
    ) == Decimal("10")

def test_sous_seuil_sans_maximum():
    assert quantite_suggeree(
        disponible=Decimal("6"), minimum=Decimal("10"),
        maximum=Decimal("0"), seuil_alerte=Decimal("10")
    ) == Decimal("4")
