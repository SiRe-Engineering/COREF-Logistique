from decimal import Decimal

from app.schemas.inventaire import LigneInventaireUpdate


def test_quantite_comptee_valide() -> None:
    ligne = LigneInventaireUpdate(quantite_comptee=Decimal("12.5"))
    assert ligne.quantite_comptee == Decimal("12.5")
