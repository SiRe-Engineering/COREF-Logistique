from decimal import Decimal
from app.schemas.demande_sortie import DemandeSortieCreate

def test_demande_sortie_valide() -> None:
    demande = DemandeSortieCreate(
        article_id=1,
        emplacement_source_id=2,
        quantite=Decimal("10"),
        motif="Besoin atelier",
    )
    assert demande.quantite == Decimal("10")
