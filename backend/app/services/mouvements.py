from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.mouvement import MouvementStock
from app.models.stock import Stock
from app.schemas.mouvement import MouvementCreate


def _charger_article(db: Session, article_id: int) -> Article:
    article = db.get(Article, article_id)
    if article is None or not article.actif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable.",
        )
    return article


def _charger_emplacement(
    db: Session,
    emplacement_id: int | None,
    libelle: str,
) -> Emplacement | None:
    if emplacement_id is None:
        return None

    emplacement = db.get(Emplacement, emplacement_id)
    if emplacement is None or not emplacement.actif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emplacement {libelle} introuvable.",
        )
    return emplacement


def _charger_stock_verrouille(
    db: Session,
    article_id: int,
    emplacement_id: int,
    creer: bool,
) -> Stock:
    stock = db.scalar(
    select(Stock)
    .where(
        Stock.article_id == article_id,
        Stock.emplacement_id == emplacement_id,
    )
    .with_for_update(of=Stock)
    )

    if stock is None:
        if not creer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Aucun stock n’existe dans l’emplacement source.",
            )

        stock = Stock(
            article_id=article_id,
            emplacement_id=emplacement_id,
            quantite_physique=Decimal("0"),
            quantite_reservee=Decimal("0"),
        )
        db.add(stock)
        db.flush()

    return stock


def _retirer(stock: Stock, quantite: Decimal) -> None:
    disponible = stock.quantite_physique - stock.quantite_reservee
    if disponible < quantite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Stock disponible insuffisant : "
                f"{disponible} disponible pour {quantite} demandé."
            ),
        )
    stock.quantite_physique -= quantite


def executer_mouvement(
    db: Session,
    payload: MouvementCreate,
) -> MouvementStock:
    _charger_article(db, payload.article_id)
    _charger_emplacement(
        db,
        payload.emplacement_source_id,
        "source",
    )
    _charger_emplacement(
        db,
        payload.emplacement_destination_id,
        "de destination",
    )

    type_mouvement = payload.type
    quantite = payload.quantite

    try:
        if type_mouvement in {
            "ENTREE",
            "RETOUR",
            "AJUSTEMENT_POSITIF",
        }:
            destination = _charger_stock_verrouille(
                db,
                payload.article_id,
                payload.emplacement_destination_id,
                creer=True,
            )
            destination.quantite_physique += quantite

        elif type_mouvement in {
            "SORTIE",
            "AJUSTEMENT_NEGATIF",
        }:
            source = _charger_stock_verrouille(
                db,
                payload.article_id,
                payload.emplacement_source_id,
                creer=False,
            )
            _retirer(source, quantite)

        elif type_mouvement == "TRANSFERT":
            ids = sorted(
                [
                    payload.emplacement_source_id,
                    payload.emplacement_destination_id,
                ]
            )

            stocks = {}
            for emplacement_id in ids:
                stocks[emplacement_id] = _charger_stock_verrouille(
                    db,
                    payload.article_id,
                    emplacement_id,
                    creer=(
                        emplacement_id
                        == payload.emplacement_destination_id
                    ),
                )

            source = stocks[payload.emplacement_source_id]
            destination = stocks[payload.emplacement_destination_id]
            _retirer(source, quantite)
            destination.quantite_physique += quantite

        mouvement = MouvementStock(**payload.model_dump())
        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)
        return mouvement

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
