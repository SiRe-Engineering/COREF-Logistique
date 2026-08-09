from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.affaire import Affaire
from app.models.article import Article
from app.models.demande_sortie import DemandeSortie
from app.models.emplacement import Emplacement
from app.models.famille import Famille
from app.models.lot_beton import LotBeton
from app.models.utilisateur import Utilisateur
from app.schemas.demande_sortie import (
    DemandeSortieCreate,
    DemandeSortieRead,
    RefusDemande,
)
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement
from app.services.notifications import creer_notification

router = APIRouter(prefix="/api/demandes-sortie", tags=["Demandes de sortie"])

ROLES_VALIDATEURS = {
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
    "RESPONSABLE_LOGISTIQUE",
    "RESPONSABLE_PRODUCTION",
    "CHARGE_AFFAIRES",
}


def charger_demande(db: Session, demande_id: int) -> DemandeSortie:
    demande = db.scalar(
        select(DemandeSortie)
        .options(
            joinedload(DemandeSortie.demandeur),
            joinedload(DemandeSortie.validateur),
            joinedload(DemandeSortie.article),
            joinedload(DemandeSortie.lot),
            joinedload(DemandeSortie.emplacement_source),
            joinedload(DemandeSortie.affaire),
        )
        .where(DemandeSortie.id == demande_id)
    )
    if demande is None:
        raise HTTPException(status_code=404, detail="Demande introuvable.")
    return demande


def mouvement_depuis_demande(
    demande: DemandeSortie,
    operateur: str,
    commentaire: str | None = None,
) -> MouvementCreate:
    return MouvementCreate(
        type="SORTIE",
        article_id=demande.article_id,
        lot_id=demande.lot_id,
        affaire_id=demande.affaire_id,
        emplacement_source_id=demande.emplacement_source_id,
        quantite=demande.quantite,
        motif=demande.motif,
        commentaire=commentaire or demande.commentaire,
        operateur=operateur,
        vehicule=demande.vehicule,
        sortie_libre=demande.affaire_id is None,
    )


def notifier_validateurs(db: Session, demande: DemandeSortie) -> None:
    validateurs = db.scalars(
        select(Utilisateur).where(
            Utilisateur.actif.is_(True),
            Utilisateur.role.in_(ROLES_VALIDATEURS),
            Utilisateur.type_compte == "METIER",
            Utilisateur.entreprise == "COREF",
        )
    ).all()

    for validateur in validateurs:
        creer_notification(
            db,
            validateur.nom_complet,
            "Sortie à valider",
            (
                f"{demande.reference} — {demande.article.reference} — "
                f"{demande.quantite} {demande.article.unite}, demandée par "
                f"{demande.demandeur.nom_complet}."
            ),
            "/demandes-sortie",
            "ACTION",
        )


@router.get("", response_model=list[DemandeSortieRead])
def lister_demandes(
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> list[DemandeSortie]:
    requete = select(DemandeSortie).order_by(
        DemandeSortie.date_creation.desc()
    )

    if utilisateur.role not in ROLES_VALIDATEURS:
        requete = requete.where(
            DemandeSortie.demandeur_id == utilisateur.id
        )

    return list(db.scalars(requete).unique().all())


@router.post("", response_model=DemandeSortieRead, status_code=status.HTTP_201_CREATED)
def creer_demande(
    payload: DemandeSortieCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> DemandeSortie:
    article = db.get(Article, payload.article_id)
    if article is None or not article.actif:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    emplacement = db.get(Emplacement, payload.emplacement_source_id)
    if emplacement is None or not emplacement.actif:
        raise HTTPException(status_code=404, detail="Emplacement introuvable.")

    if payload.affaire_id is not None:
        affaire = db.get(Affaire, payload.affaire_id)
        if affaire is None or not affaire.actif:
            raise HTTPException(status_code=404, detail="Affaire introuvable.")
        if affaire.statut in {"TERMINEE", "ANNULEE"}:
            raise HTTPException(status_code=409, detail="Affaire clôturée.")

    famille = db.get(Famille, article.famille_id) if article.famille_id else None
    if famille is not None and famille.code == "BET" and payload.lot_id is None:
        raise HTTPException(status_code=422, detail="Un lot est obligatoire pour un béton.")

    if payload.lot_id is not None:
        lot = db.get(LotBeton, payload.lot_id)
        if lot is None or lot.article_id != article.id:
            raise HTTPException(status_code=422, detail="Lot incompatible.")

    demande = DemandeSortie(
        demandeur_id=utilisateur.id,
        **payload.model_dump(),
        statut="EN_ATTENTE",
    )
    db.add(demande)
    db.flush()
    db.refresh(demande)

    if utilisateur.role in ROLES_VALIDATEURS:
        executer_mouvement(
            db,
            mouvement_depuis_demande(demande, utilisateur.nom_complet),
        )
        demande.statut = "APPROUVEE"
        demande.validateur_id = utilisateur.id
        demande.date_decision = datetime.now(timezone.utc)
    else:
        notifier_validateurs(db, demande)

    db.commit()
    return charger_demande(db, demande.id)


@router.post("/{demande_id}/approuver", response_model=DemandeSortieRead)
def approuver_demande(
    demande_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> DemandeSortie:
    if utilisateur.role not in ROLES_VALIDATEURS:
        raise HTTPException(status_code=403, detail="Droits insuffisants.")

    demande = charger_demande(db, demande_id)
    if demande.statut != "EN_ATTENTE":
        raise HTTPException(status_code=409, detail="Demande déjà traitée.")

    try:
        executer_mouvement(
            db,
            mouvement_depuis_demande(
                demande,
                demande.demandeur.nom_complet,
                (
                    f"{demande.commentaire or ''}\nDemande {demande.reference} "
                    f"approuvée par {utilisateur.nom_complet}."
                ).strip(),
            ),
        )
        demande.statut = "APPROUVEE"
        demande.validateur_id = utilisateur.id
        demande.date_decision = datetime.now(timezone.utc)

        creer_notification(
            db,
            demande.demandeur.nom_complet,
            "Sortie approuvée",
            f"{demande.reference} a été approuvée par {utilisateur.nom_complet}.",
            "/demandes-sortie",
            "INFORMATION",
        )
        db.commit()
        return charger_demande(db, demande.id)
    except HTTPException:
        db.rollback()
        raise


@router.post("/{demande_id}/refuser", response_model=DemandeSortieRead)
def refuser_demande(
    demande_id: int,
    payload: RefusDemande,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> DemandeSortie:
    if utilisateur.role not in ROLES_VALIDATEURS:
        raise HTTPException(status_code=403, detail="Droits insuffisants.")

    demande = charger_demande(db, demande_id)
    if demande.statut != "EN_ATTENTE":
        raise HTTPException(status_code=409, detail="Demande déjà traitée.")

    demande.statut = "REFUSEE"
    demande.validateur_id = utilisateur.id
    demande.date_decision = datetime.now(timezone.utc)
    demande.motif_refus = payload.motif_refus

    creer_notification(
        db,
        demande.demandeur.nom_complet,
        "Sortie refusée",
        (
            f"{demande.reference} a été refusée par "
            f"{utilisateur.nom_complet} : {payload.motif_refus}"
        ),
        "/demandes-sortie",
        "ALERTE",
    )
    db.commit()
    return charger_demande(db, demande.id)
