from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.dependencies import exiger_roles
from app.models.article import Article
from app.models.mouvement import MouvementStock
from app.models.utilisateur import Utilisateur
from app.schemas.mouvement import (
    AnnulationMouvementCreate,
    MouvementCreate,
    MouvementRead,
)
from app.services.mouvements import annuler_mouvement, executer_mouvement

router = APIRouter(
    prefix="/api/mouvements",
    tags=["Mouvements"],
)


@router.get("", response_model=list[MouvementRead])
def lister_mouvements(
    recherche: str | None = Query(default=None, max_length=100),
    article_id: int | None = None,
    lot_id: int | None = None,
    affaire_id: int | None = None,
    type_mouvement: str | None = None,
    emplacement_id: int | None = None,
    limite: int = Query(default=200, ge=1, le=1000),
    inclure_annules: bool = False,
    db: Session = Depends(get_db),
) -> list[MouvementStock]:
    requete = (
        select(MouvementStock)
        .join(MouvementStock.article)
        .options(
            joinedload(MouvementStock.article),
            joinedload(MouvementStock.lot),
            joinedload(MouvementStock.affaire),
            joinedload(MouvementStock.emplacement_source),
            joinedload(MouvementStock.emplacement_destination),
        )
        .order_by(MouvementStock.date_creation.desc())
        .limit(limite)
    )

    if not inclure_annules:
        requete = requete.where(MouvementStock.annule.is_(False))

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                MouvementStock.reference.ilike(terme),
                Article.reference.ilike(terme),
                Article.designation.ilike(terme),
                MouvementStock.motif.ilike(terme),
                MouvementStock.charge_affaires.ilike(terme),
                MouvementStock.zone_intervention.ilike(terme),
            )
        )

    if article_id is not None:
        requete = requete.where(
            MouvementStock.article_id == article_id
        )

    if lot_id is not None:
        requete = requete.where(MouvementStock.lot_id == lot_id)

    if affaire_id is not None:
        requete = requete.where(
            MouvementStock.affaire_id == affaire_id
        )

    if type_mouvement:
        requete = requete.where(
            MouvementStock.type == type_mouvement.upper()
        )

    if emplacement_id is not None:
        requete = requete.where(
            or_(
                MouvementStock.emplacement_source_id == emplacement_id,
                MouvementStock.emplacement_destination_id
                == emplacement_id,
            )
        )

    return list(db.scalars(requete).unique().all())


@router.post(
    "",
    response_model=MouvementRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_mouvement(
    payload: MouvementCreate,
    db: Session = Depends(get_db),
) -> MouvementStock:
    return executer_mouvement(db, payload)



@router.delete("/{mouvement_id}", response_model=MouvementRead)
def supprimer_ecriture_stock(
    mouvement_id: int,
    payload: AnnulationMouvementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        exiger_roles("ADMINISTRATEUR_TECHNIQUE")
    ),
) -> MouvementStock:
    mouvement = db.scalar(
        select(MouvementStock)
        .where(MouvementStock.id == mouvement_id)
        .with_for_update(of=MouvementStock)
    )
    if mouvement is None:
        raise HTTPException(
            status_code=404,
            detail="Écriture de stock introuvable.",
        )

    return annuler_mouvement(
        db,
        mouvement,
        annule_par=utilisateur.nom_complet,
        motif=payload.motif,
    )
