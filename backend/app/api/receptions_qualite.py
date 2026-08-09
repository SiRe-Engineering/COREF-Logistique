from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.reception_achat import ReceptionAchat
from app.models.non_conformite_fournisseur import NonConformiteFournisseur
from app.models.utilisateur import Utilisateur


router = APIRouter(
    prefix="/api/receptions-qualite",
    tags=["Réceptions qualité"],
)


@router.get("")
def lister(
    statut: str | None = None,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    q = select(ReceptionAchat).order_by(
        ReceptionAchat.date_reception.desc()
    )
    if statut:
        q = q.where(ReceptionAchat.statut_qualite == statut)

    receptions = list(db.scalars(q).unique().all())
    ncf_by_reception={x.reception_id:x for x in db.scalars(select(NonConformiteFournisseur)).all()}
    return [
        {
            "id": r.id,
            "commande_id": r.commande_id,
            "commande_reference": r.commande.reference,
            "fournisseur": r.commande.fournisseur.raison_sociale,
            "article_reference": r.article.reference,
            "article_designation": r.article.designation,
            "lot_beton_id": r.lot_beton_id,
            "lot_reference": (
                r.lot_beton.reference_interne if r.lot_beton else None
            ),
            "quantite": r.quantite,
            "unite": r.article.unite,
            "bon_livraison_reference": r.bon_livraison_reference,
            "conformite_visuelle": r.conformite_visuelle,
            "reserve_commentaire": r.reserve_commentaire,
            "commentaire_qualite": r.commentaire_qualite,
            "fds_presente": r.fds_presente,
            "statut_qualite": r.statut_qualite,
            "receptionne_par": r.receptionne_par,
            "date_reception": r.date_reception,
            "ncf_id": ncf_by_reception[r.id].id if r.id in ncf_by_reception else None,
            "ncf_reference": ncf_by_reception[r.id].reference if r.id in ncf_by_reception else None,
        }
        for r in receptions
    ]
