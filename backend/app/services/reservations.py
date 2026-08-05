from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lot_beton import StockLot
from app.models.preparation import LignePreparation, Preparation
from app.models.reservation import ReservationStock
from app.models.stock import Stock


def _stock_article(
    db: Session,
    article_id: int,
    emplacement_id: int,
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
        raise HTTPException(
            status_code=409,
            detail="Aucun stock n’existe dans l’emplacement sélectionné.",
        )
    return stock


def _stock_lot(
    db: Session,
    lot_id: int,
    emplacement_id: int,
) -> StockLot:
    stock_lot = db.scalar(
        select(StockLot)
        .where(
            StockLot.lot_id == lot_id,
            StockLot.emplacement_id == emplacement_id,
        )
        .with_for_update(of=StockLot)
    )
    if stock_lot is None:
        raise HTTPException(
            status_code=409,
            detail="Le lot n’est pas présent dans cet emplacement.",
        )
    return stock_lot


def _appliquer_quantite_reservee(
    db: Session,
    ligne: LignePreparation,
    ancienne_quantite: Decimal,
    nouvelle_quantite: Decimal,
) -> None:
    if ligne.emplacement_source_id is None:
        raise HTTPException(
            status_code=422,
            detail=f"{ligne.article.reference} : emplacement source manquant.",
        )

    delta = nouvelle_quantite - ancienne_quantite
    if delta == 0:
        return

    stock = _stock_article(
        db,
        ligne.article_id,
        ligne.emplacement_source_id,
    )
    disponible_avant = stock.quantite_physique - stock.quantite_reservee

    if delta > 0 and disponible_avant < delta:
        raise HTTPException(
            status_code=409,
            detail=(
                f"{ligne.article.reference} : stock disponible insuffisant "
                f"pour réserver {delta} supplémentaire."
            ),
        )

    stock.quantite_reservee += delta
    if stock.quantite_reservee < 0:
        stock.quantite_reservee = Decimal("0")

    if ligne.lot_id is not None:
        stock_lot = _stock_lot(
            db,
            ligne.lot_id,
            ligne.emplacement_source_id,
        )
        disponible_lot = (
            stock_lot.quantite_physique - stock_lot.quantite_reservee
        )
        if delta > 0 and disponible_lot < delta:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{ligne.article.reference} : stock du lot insuffisant "
                    f"pour réserver {delta} supplémentaire."
                ),
            )
        stock_lot.quantite_reservee += delta
        if stock_lot.quantite_reservee < 0:
            stock_lot.quantite_reservee = Decimal("0")


def synchroniser_reservation_ligne(
    db: Session,
    preparation: Preparation,
    ligne: LignePreparation,
) -> ReservationStock:
    reservation = db.scalar(
        select(ReservationStock).where(
            ReservationStock.ligne_preparation_id == ligne.id
        )
    )
    ancienne_quantite = (
        reservation.quantite
        if reservation is not None and reservation.statut == "ACTIVE"
        else Decimal("0")
    )

    _appliquer_quantite_reservee(
        db,
        ligne,
        ancienne_quantite,
        ligne.quantite_demandee,
    )

    if reservation is None:
        reservation = ReservationStock(
            article_id=ligne.article_id,
            lot_id=ligne.lot_id,
            emplacement_id=ligne.emplacement_source_id,
            preparation_id=preparation.id,
            ligne_preparation_id=ligne.id,
            quantite=ligne.quantite_demandee,
            reserve_pour=(
                f"{preparation.reference} — "
                f"{preparation.affaire.code_externe or preparation.affaire.reference}"
            ),
            reserve_par=preparation.demandeur,
            motif=preparation.nom,
            statut="ACTIVE",
        )
        db.add(reservation)
    else:
        reservation.article_id = ligne.article_id
        reservation.lot_id = ligne.lot_id
        reservation.emplacement_id = ligne.emplacement_source_id
        reservation.quantite = ligne.quantite_demandee
        reservation.reserve_pour = (
            f"{preparation.reference} — "
            f"{preparation.affaire.code_externe or preparation.affaire.reference}"
        )
        reservation.reserve_par = preparation.demandeur
        reservation.motif = preparation.nom
        reservation.statut = "ACTIVE"
        reservation.date_liberation = None

    return reservation


def liberer_reservation_ligne(
    db: Session,
    ligne: LignePreparation,
) -> None:
    reservation = db.scalar(
        select(ReservationStock).where(
            ReservationStock.ligne_preparation_id == ligne.id,
            ReservationStock.statut == "ACTIVE",
        )
    )
    if reservation is None:
        return

    _appliquer_quantite_reservee(
        db,
        ligne,
        reservation.quantite,
        Decimal("0"),
    )
    reservation.statut = "LIBEREE"
    reservation.date_liberation = datetime.now(timezone.utc)


def liberer_reservations_preparation(
    db: Session,
    preparation: Preparation,
) -> None:
    for ligne in preparation.lignes:
        liberer_reservation_ligne(db, ligne)
