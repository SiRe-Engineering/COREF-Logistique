from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.models.achats import ArticleFournisseur
from app.models.reapprovisionnement import BesoinReapprovisionnement
from app.models.utilisateur import Utilisateur
from app.schemas.mouvement import MouvementCreate
from app.schemas.reapprovisionnement import (
    BesoinCreate,
    BesoinRead,
    BesoinUpdate,
    ReceptionCreate,
    SuggestionReapproRead,
)
from app.services.mouvements import executer_mouvement
from app.services.reapprovisionnement import (
    STATUTS_OUVERTS,
    quantite_suggeree,
    suggestions_reapprovisionnement,
)


router = APIRouter(
    prefix="/api/reapprovisionnement",
    tags=["Réapprovisionnement"],
)


def _besoin(db: Session, besoin_id: int) -> BesoinReapprovisionnement:
    besoin = db.scalar(
        select(BesoinReapprovisionnement)
        .options(joinedload(BesoinReapprovisionnement.article))
        .where(BesoinReapprovisionnement.id == besoin_id)
    )
    if besoin is None:
        raise HTTPException(status_code=404, detail="Besoin introuvable.")
    return besoin


def _disponible_article(db: Session, article_id: int) -> Decimal:
    from sqlalchemy import func
    from app.models.stock import Stock

    physique, reservee = db.execute(
        select(
            func.coalesce(func.sum(Stock.quantite_physique), 0),
            func.coalesce(func.sum(Stock.quantite_reservee), 0),
        ).where(Stock.article_id == article_id)
    ).one()
    return Decimal(physique or 0) - Decimal(reservee or 0)


@router.get("/suggestions", response_model=list[SuggestionReapproRead])
def lister_suggestions(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> list[SuggestionReapproRead]:
    return suggestions_reapprovisionnement(db)


@router.get("/besoins", response_model=list[BesoinRead])
def lister_besoins(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> list[BesoinReapprovisionnement]:
    return list(
        db.scalars(
            select(BesoinReapprovisionnement)
            .options(joinedload(BesoinReapprovisionnement.article))
            .order_by(BesoinReapprovisionnement.date_creation.desc())
        ).unique().all()
    )


@router.post(
    "/besoins",
    response_model=BesoinRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_besoin(
    payload: BesoinCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> BesoinReapprovisionnement:
    article = db.get(Article, payload.article_id)
    if article is None or not article.actif:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    existant = db.scalar(
        select(BesoinReapprovisionnement).where(
            BesoinReapprovisionnement.article_id == article.id,
            BesoinReapprovisionnement.statut.in_(STATUTS_OUVERTS),
        )
    )
    if existant is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Un besoin ouvert existe déjà pour cet article "
                f"({existant.reference})."
            ),
        )

    disponible = _disponible_article(db, article.id)
    suggeree = quantite_suggeree(
        disponible=disponible,
        minimum=Decimal(article.stock_minimum or 0),
        maximum=Decimal(article.stock_maximum or 0),
        seuil_alerte=Decimal(article.seuil_alerte or 0),
    )
    demandee = payload.quantite_demandee or suggeree
    if demandee <= 0:
        raise HTTPException(
            status_code=422,
            detail="La quantité à réapprovisionner doit être positive.",
        )

    prefere = db.scalar(
        select(ArticleFournisseur).where(
            ArticleFournisseur.article_id == article.id,
            ArticleFournisseur.fournisseur_prefere.is_(True),
        )
    )

    prix_prevu = (
        prefere.prix_unitaire_ht
        if prefere is not None and prefere.prix_unitaire_ht is not None
        else payload.prix_unitaire_prevu
        if payload.prix_unitaire_prevu is not None
        else article.dernier_prix_achat
    )
    fournisseur_prevu = (
        prefere.fournisseur.raison_sociale
        if prefere is not None
        else payload.fournisseur
    )

    besoin = BesoinReapprovisionnement(
        article_id=article.id,
        quantite_suggeree=suggeree,
        quantite_demandee=demandee,
        prix_unitaire_prevu=prix_prevu,
        fournisseur=fournisseur_prevu,
        commentaire=payload.commentaire,
        cree_par=utilisateur.nom_complet,
    )
    db.add(besoin)
    db.commit()
    db.refresh(besoin)
    return besoin


@router.patch("/besoins/{besoin_id}", response_model=BesoinRead)
def modifier_besoin(
    besoin_id: int,
    payload: BesoinUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> BesoinReapprovisionnement:
    besoin = _besoin(db, besoin_id)
    if besoin.statut in {"RECU", "ANNULE"}:
        raise HTTPException(
            status_code=409,
            detail="Ce besoin est clôturé.",
        )

    donnees = payload.model_dump(exclude_unset=True)
    ancien_statut = besoin.statut
    for champ, valeur in donnees.items():
        setattr(besoin, champ, valeur)

    maintenant = datetime.now(timezone.utc)
    if besoin.statut == "VALIDE" and ancien_statut != "VALIDE":
        besoin.date_validation = maintenant
    if besoin.statut == "COMMANDE" and ancien_statut != "COMMANDE":
        if besoin.quantite_commandee <= 0:
            besoin.quantite_commandee = besoin.quantite_demandee
        besoin.date_commande = maintenant
    if besoin.statut == "ANNULE":
        besoin.date_cloture = maintenant

    db.commit()
    db.refresh(besoin)
    return besoin


@router.post(
    "/besoins/{besoin_id}/reception",
    response_model=BesoinRead,
)
def receptionner(
    besoin_id: int,
    payload: ReceptionCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> BesoinReapprovisionnement:
    besoin = _besoin(db, besoin_id)
    if besoin.statut == "ANNULE":
        raise HTTPException(status_code=409, detail="Ce besoin est annulé.")
    if besoin.statut == "RECU":
        raise HTTPException(status_code=409, detail="Ce besoin est déjà reçu.")

    restant = max(
        Decimal("0"),
        besoin.quantite_commandee - besoin.quantite_recue,
    )
    # If no explicit ordered quantity exists, requested quantity is the
    # reception ceiling.
    plafond = restant if besoin.quantite_commandee > 0 else (
        besoin.quantite_demandee - besoin.quantite_recue
    )
    if payload.quantite > plafond:
        raise HTTPException(
            status_code=422,
            detail=f"Réception supérieure au solde attendu ({plafond}).",
        )

    executer_mouvement(
        db,
        MouvementCreate(
            type="ENTREE",
            article_id=besoin.article_id,
            lot_id=payload.lot_id,
            besoin_reapprovisionnement_id=besoin.id,
            emplacement_destination_id=payload.emplacement_destination_id,
            quantite=payload.quantite,
            prix_unitaire_ht=payload.prix_unitaire_ht,
            motif=f"Réception {besoin.reference}",
            commentaire=payload.commentaire,
            operateur=utilisateur.nom_complet,
        ),
        valider_transaction=False,
    )

    besoin.quantite_recue += payload.quantite
    attendu = (
        besoin.quantite_commandee
        if besoin.quantite_commandee > 0
        else besoin.quantite_demandee
    )
    if besoin.quantite_recue >= attendu:
        besoin.statut = "RECU"
        besoin.date_cloture = datetime.now(timezone.utc)
    else:
        besoin.statut = "COMMANDE"

    db.commit()
    db.refresh(besoin)
    return besoin
