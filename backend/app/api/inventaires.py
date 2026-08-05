from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.inventaire import Inventaire, LigneInventaire
from app.models.lot_beton import StockLot
from app.models.stock import Stock
from app.schemas.inventaire import (
    InventaireCreate,
    InventaireRead,
    LigneInventaireUpdate,
)
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement

router = APIRouter(prefix="/api/inventaires", tags=["Inventaires"])


def charger_inventaire(db: Session, inventaire_id: int) -> Inventaire:
    inventaire = db.scalar(
        select(Inventaire)
        .options(
            selectinload(Inventaire.lignes),
        )
        .where(Inventaire.id == inventaire_id)
    )
    if inventaire is None:
        raise HTTPException(status_code=404, detail="Inventaire introuvable.")
    return inventaire


@router.get("", response_model=list[InventaireRead])
def lister_inventaires(db: Session = Depends(get_db)) -> list[Inventaire]:
    return list(
        db.scalars(
            select(Inventaire)
            .options(selectinload(Inventaire.lignes))
            .order_by(Inventaire.date_creation.desc())
        ).unique().all()
    )


@router.post(
    "",
    response_model=InventaireRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_inventaire(
    payload: InventaireCreate,
    db: Session = Depends(get_db),
) -> Inventaire:
    emplacement = db.get(Emplacement, payload.emplacement_id)
    if emplacement is None or not emplacement.actif:
        raise HTTPException(status_code=404, detail="Emplacement introuvable.")

    inventaire = Inventaire(
        **payload.model_dump(),
        statut="EN_COURS",
    )
    db.add(inventaire)
    db.flush()

    stocks = list(
        db.scalars(
            select(Stock).where(Stock.emplacement_id == payload.emplacement_id)
        ).all()
    )

    for stock in stocks:
        article = db.get(Article, stock.article_id)
        if article is None:
            continue

        lots = list(
            db.scalars(
                select(StockLot).where(
                    StockLot.emplacement_id == payload.emplacement_id,
                    StockLot.lot.has(article_id=article.id),
                    StockLot.quantite_physique > 0,
                )
            ).all()
        )

        if lots:
            for stock_lot in lots:
                inventaire.lignes.append(
                    LigneInventaire(
                        article_id=article.id,
                        lot_id=stock_lot.lot_id,
                        quantite_theorique=stock_lot.quantite_physique,
                    )
                )
        else:
            inventaire.lignes.append(
                LigneInventaire(
                    article_id=article.id,
                    lot_id=None,
                    quantite_theorique=stock.quantite_physique,
                )
            )

    db.commit()
    db.refresh(inventaire)
    return inventaire


@router.patch(
    "/{inventaire_id}/lignes/{ligne_id}",
    response_model=InventaireRead,
)
def saisir_comptage(
    inventaire_id: int,
    ligne_id: int,
    payload: LigneInventaireUpdate,
    db: Session = Depends(get_db),
) -> Inventaire:
    inventaire = charger_inventaire(db, inventaire_id)

    if inventaire.statut != "EN_COURS":
        raise HTTPException(
            status_code=409,
            detail="Cet inventaire ne peut plus être modifié.",
        )

    ligne = next(
        (element for element in inventaire.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")

    ligne.quantite_comptee = payload.quantite_comptee
    ligne.commentaire = payload.commentaire
    db.commit()
    return charger_inventaire(db, inventaire_id)


@router.post("/{inventaire_id}/valider", response_model=InventaireRead)
def valider_inventaire(
    inventaire_id: int,
    db: Session = Depends(get_db),
) -> Inventaire:
    inventaire = charger_inventaire(db, inventaire_id)

    if inventaire.statut != "EN_COURS":
        raise HTTPException(
            status_code=409,
            detail="Cet inventaire est déjà clôturé.",
        )

    non_comptees = [
        ligne for ligne in inventaire.lignes if ligne.quantite_comptee is None
    ]
    if non_comptees:
        raise HTTPException(
            status_code=422,
            detail="Toutes les lignes doivent être comptées avant validation.",
        )

    try:
        for ligne in inventaire.lignes:
            ecart = ligne.ecart or Decimal("0")
            if ecart == 0:
                continue

            mouvement = MouvementCreate(
                type=(
                    "AJUSTEMENT_POSITIF"
                    if ecart > 0
                    else "AJUSTEMENT_NEGATIF"
                ),
                article_id=ligne.article_id,
                lot_id=ligne.lot_id,
                emplacement_source_id=(
                    inventaire.emplacement_id if ecart < 0 else None
                ),
                emplacement_destination_id=(
                    inventaire.emplacement_id if ecart > 0 else None
                ),
                quantite=abs(ecart),
                motif=f"Validation {inventaire.reference}",
                commentaire=ligne.commentaire,
                operateur=inventaire.operateur,
            )
            executer_mouvement(db, mouvement)

        inventaire = charger_inventaire(db, inventaire_id)
        inventaire.statut = "VALIDE"
        inventaire.date_validation = datetime.now(timezone.utc)
        db.commit()
        return charger_inventaire(db, inventaire_id)

    except HTTPException:
        db.rollback()
        raise
