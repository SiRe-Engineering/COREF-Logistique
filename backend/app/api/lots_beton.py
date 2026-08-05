from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.article import Article
from app.models.famille import Famille
from app.models.lot_beton import LotBeton
from app.schemas.lot_beton import (
    LotBetonCreate,
    LotBetonRead,
    LotBetonUpdate,
)

router = APIRouter(
    prefix="/api/lots-beton",
    tags=["Lots béton"],
)


def verifier_article_beton(db: Session, article_id: int) -> Article:
    article = db.get(Article, article_id)
    if article is None or not article.actif:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    famille = db.get(Famille, article.famille_id) if article.famille_id else None
    if famille is None or famille.code != "BET":
        raise HTTPException(
            status_code=422,
            detail="Les lots renforcés sont réservés aux articles Béton.",
        )

    return article


@router.get("", response_model=list[LotBetonRead])
def lister_lots(
    recherche: str | None = Query(default=None, max_length=100),
    article_id: int | None = None,
    actifs_uniquement: bool = True,
    expires_avant: date | None = None,
    db: Session = Depends(get_db),
) -> list[LotBeton]:
    requete = (
        select(LotBeton)
        .join(LotBeton.article)
        .options(
            selectinload(LotBeton.stocks),
        )
        .order_by(
            LotBeton.date_peremption,
            LotBeton.reference_interne,
        )
    )

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                LotBeton.reference_interne.ilike(terme),
                LotBeton.numero_lot_fournisseur.ilike(terme),
                LotBeton.fournisseur.ilike(terme),
                Article.reference.ilike(terme),
                Article.designation.ilike(terme),
            )
        )

    if article_id is not None:
        requete = requete.where(LotBeton.article_id == article_id)

    if actifs_uniquement:
        requete = requete.where(LotBeton.actif.is_(True))

    if expires_avant is not None:
        requete = requete.where(
            LotBeton.date_peremption <= expires_avant
        )

    return list(db.scalars(requete).unique().all())


@router.post(
    "",
    response_model=LotBetonRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_lot(
    payload: LotBetonCreate,
    db: Session = Depends(get_db),
) -> LotBeton:
    verifier_article_beton(db, payload.article_id)

    lot = LotBeton(**payload.model_dump())
    db.add(lot)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Ce numéro de lot fournisseur existe déjà pour cet article."
            ),
        )

    db.refresh(lot)
    return lot


@router.patch("/{lot_id}", response_model=LotBetonRead)
def modifier_lot(
    lot_id: int,
    payload: LotBetonUpdate,
    db: Session = Depends(get_db),
) -> LotBeton:
    lot = db.get(LotBeton, lot_id)
    if lot is None:
        raise HTTPException(status_code=404, detail="Lot introuvable.")

    donnees = payload.model_dump(exclude_unset=True)
    date_fabrication = donnees.get(
        "date_fabrication",
        lot.date_fabrication,
    )
    date_peremption = donnees.get(
        "date_peremption",
        lot.date_peremption,
    )

    if date_peremption < date_fabrication:
        raise HTTPException(
            status_code=422,
            detail="Les dates de fabrication et péremption sont incohérentes.",
        )

    for champ, valeur in donnees.items():
        setattr(lot, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Ce numéro de lot fournisseur existe déjà pour cet article."
            ),
        )

    db.refresh(lot)
    return lot
