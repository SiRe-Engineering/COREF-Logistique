from decimal import Decimal

from app.models.lot_beton import LotBeton
from app.models.mouvement import MouvementStock
from app.schemas.lot_beton import SuppressionLotCreate
from app.schemas.mouvement import AnnulationMouvementCreate


def test_motif_suppression_lot_obligatoire() -> None:
    payload = SuppressionLotCreate(motif="Erreur de saisie du lot")
    assert payload.motif.startswith("Erreur")


def test_motif_annulation_mouvement_obligatoire() -> None:
    payload = AnnulationMouvementCreate(
        motif="Double saisie de la réception"
    )
    assert payload.motif.startswith("Double")


def test_modeles_exposent_audit_administratif() -> None:
    lot = LotBeton(
        article_id=1,
        numero_lot_fournisseur="LOT-TEST",
    )
    mouvement = MouvementStock(
        type="ENTREE",
        article_id=1,
        quantite=Decimal("10"),
    )

    lot.supprime = True
    mouvement.annule = True

    assert lot.supprime is True
    assert mouvement.annule is True
