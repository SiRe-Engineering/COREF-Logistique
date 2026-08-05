from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.stock import Stock
from app.schemas.stock import StockRead, StockResume, StockSet

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])


@router.get("", response_model=list[StockRead])
def lister_stocks(
    recherche: str | None = Query(default=None, max_length=100),
    article_id: int | None = None,
    emplacement_id: int | None = None,
    alertes_uniquement: bool = False,
    db: Session = Depends(get_db),
) -> list[Stock]:
    requete = (
        select(Stock)
        .join(Stock.article)
        .join(Stock.emplacement)
        .options(
            joinedload(Stock.article),
            joinedload(Stock.emplacement),
        )
        .where(Article.actif.is_(True))
        .where(Emplacement.actif.is_(True))
        .order_by(Article.reference, Emplacement.code)
    )

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                Article.reference.ilike(terme),
                Article.designation.ilike(terme),
                Emplacement.code.ilike(terme),
                Emplacement.nom.ilike(terme),
            )
        )
    if article_id is not None:
        requete = requete.where(Stock.article_id == article_id)
    if emplacement_id is not None:
        requete = requete.where(Stock.emplacement_id == emplacement_id)
    if alertes_uniquement:
        requete = requete.where(
            (Stock.quantite_physique - Stock.quantite_reservee)
            <= func.greatest(Article.seuil_alerte, Article.stock_minimum)
        )

    return list(db.scalars(requete).unique().all())


@router.get("/resume", response_model=StockResume)
def resume_stocks(db: Session = Depends(get_db)) -> StockResume:
    lignes = list(
        db.scalars(
            select(Stock)
            .join(Stock.article)
            .where(Article.actif.is_(True))
        ).all()
    )

    articles_stockes = len({ligne.article_id for ligne in lignes})
    totaux: dict[int, tuple[Article, float]] = {}

    for ligne in lignes:
        article, total = totaux.get(ligne.article_id, (ligne.article, 0.0))
        total += float(ligne.quantite_disponible)
        totaux[ligne.article_id] = (article, total)

    ruptures = 0
    alertes = 0
    for article, disponible in totaux.values():
        if disponible <= 0:
            ruptures += 1
        elif disponible <= float(
            max(article.seuil_alerte, article.stock_minimum)
        ):
            alertes += 1

    return StockResume(
        lignes_stock=len(lignes),
        articles_stockes=articles_stockes,
        ruptures=ruptures,
        alertes=alertes,
    )


@router.put("", response_model=StockRead)
def definir_stock(
    payload: StockSet,
    db: Session = Depends(get_db),
) -> Stock:
    article = db.get(Article, payload.article_id)
    if article is None or not article.actif:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    emplacement = db.get(Emplacement, payload.emplacement_id)
    if emplacement is None or not emplacement.actif:
        raise HTTPException(status_code=404, detail="Emplacement introuvable.")

    stock = db.scalar(
        select(Stock).where(
            Stock.article_id == payload.article_id,
            Stock.emplacement_id == payload.emplacement_id,
        )
    )

    if stock is None:
        stock = Stock(
            article_id=payload.article_id,
            emplacement_id=payload.emplacement_id,
        )
        db.add(stock)

    if payload.quantite_physique < stock.quantite_reservee:
        raise HTTPException(
            status_code=409,
            detail=(
                "La quantité physique ne peut pas être inférieure aux "
                "réservations actives. Libérez d’abord les réservations."
            ),
        )

    stock.quantite_physique = payload.quantite_physique
    db.commit()
    db.refresh(stock)
    return stock
