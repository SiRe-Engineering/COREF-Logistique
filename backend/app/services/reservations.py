from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lot_beton import StockLot
from app.models.preparation import LignePreparation, Preparation
from app.models.reservation import ReservationStock
from app.models.stock import Stock


def _decimal(value: Decimal | None) -> Decimal:
    return value if value is not None else Decimal("0")


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


def _appliquer_delta(
    db: Session,
    *,
    article_id: int,
    lot_id: int | None,
    emplacement_id: int,
    reference_article: str,
    delta: Decimal,
) -> None:
    if delta == 0:
        return

    stock = _stock_article(db, article_id, emplacement_id)
    stock.quantite_physique = _decimal(stock.quantite_physique)
    stock.quantite_reservee = _decimal(stock.quantite_reservee)

    disponible = stock.quantite_physique - stock.quantite_reservee
    if delta > 0 and disponible < delta:
        raise HTTPException(
            status_code=409,
            detail=(
                f"{reference_article} : stock disponible insuffisant "
                f"pour réserver {delta}."
            ),
        )

    nouvelle_reservation = stock.quantite_reservee + delta
    if nouvelle_reservation < 0:
        raise HTTPException(
            status_code=409,
            detail=f"{reference_article} : réservation article incohérente.",
        )

    if lot_id is not None:
        stock_lot = _stock_lot(db, lot_id, emplacement_id)
        stock_lot.quantite_physique = _decimal(
            stock_lot.quantite_physique
        )
        stock_lot.quantite_reservee = _decimal(
            stock_lot.quantite_reservee
        )

        disponible_lot = (
            stock_lot.quantite_physique - stock_lot.quantite_reservee
        )
        if delta > 0 and disponible_lot < delta:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{reference_article} : stock du lot insuffisant "
                    f"pour réserver {delta}."
                ),
            )

        nouvelle_reservation_lot = stock_lot.quantite_reservee + delta
        if nouvelle_reservation_lot < 0:
            raise HTTPException(
                status_code=409,
                detail=f"{reference_article} : réservation lot incohérente.",
            )
        stock_lot.quantite_reservee = nouvelle_reservation_lot

    stock.quantite_reservee = nouvelle_reservation


def _reservation_active(
    db: Session,
    ligne_id: int,
) -> ReservationStock | None:
    return db.scalar(
        select(ReservationStock)
        .where(
            ReservationStock.ligne_preparation_id == ligne_id,
            ReservationStock.statut == "ACTIVE",
        )
        .with_for_update(of=ReservationStock)
    )


def synchroniser_reservation_ligne(
    db: Session,
    preparation: Preparation,
    ligne: LignePreparation,
) -> ReservationStock:
    if ligne.emplacement_source_id is None:
        raise HTTPException(
            status_code=422,
            detail=f"{ligne.article.reference} : emplacement source manquant.",
        )

    reservation = _reservation_active(db, ligne.id)

    if reservation is not None:
        meme_cible = (
            reservation.article_id == ligne.article_id
            and reservation.lot_id == ligne.lot_id
            and reservation.emplacement_id
            == ligne.emplacement_source_id
        )

        if meme_cible:
            _appliquer_delta(
                db,
                article_id=reservation.article_id,
                lot_id=reservation.lot_id,
                emplacement_id=reservation.emplacement_id,
                reference_article=reservation.article.reference,
                delta=ligne.quantite_demandee - reservation.quantite,
            )
        else:
            _appliquer_delta(
                db,
                article_id=reservation.article_id,
                lot_id=reservation.lot_id,
                emplacement_id=reservation.emplacement_id,
                reference_article=reservation.article.reference,
                delta=-reservation.quantite,
            )
            _appliquer_delta(
                db,
                article_id=ligne.article_id,
                lot_id=ligne.lot_id,
                emplacement_id=ligne.emplacement_source_id,
                reference_article=ligne.article.reference,
                delta=ligne.quantite_demandee,
            )
    else:
        _appliquer_delta(
            db,
            article_id=ligne.article_id,
            lot_id=ligne.lot_id,
            emplacement_id=ligne.emplacement_source_id,
            reference_article=ligne.article.reference,
            delta=ligne.quantite_demandee,
        )

    reserve_pour = (
        f"{preparation.reference} — "
        f"{preparation.affaire.code_externe or preparation.affaire.reference}"
    )

    if reservation is None:
        reservation = ReservationStock(
            article_id=ligne.article_id,
            lot_id=ligne.lot_id,
            emplacement_id=ligne.emplacement_source_id,
            preparation_id=preparation.id,
            ligne_preparation_id=ligne.id,
            quantite=ligne.quantite_demandee,
            reserve_pour=reserve_pour,
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
        reservation.reserve_pour = reserve_pour
        reservation.reserve_par = preparation.demandeur
        reservation.motif = preparation.nom
        reservation.statut = "ACTIVE"
        reservation.date_liberation = None

    return reservation


def transferer_reservation_remplacement(
    db: Session,
    preparation: Preparation,
    ligne: LignePreparation,
    reserve_par: str | None,
) -> ReservationStock:
    if (
        ligne.article_remplacement_id is None
        or ligne.emplacement_remplacement_id is None
        or ligne.quantite_remplacement is None
        or ligne.article_remplacement is None
    ):
        raise HTTPException(
            status_code=422,
            detail="La proposition de remplacement est incomplète.",
        )

    reservation = _reservation_active(db, ligne.id)
    if reservation is None:
        raise HTTPException(
            status_code=409,
            detail="La réservation initiale de cette ligne est introuvable.",
        )

    _appliquer_delta(
        db,
        article_id=ligne.article_remplacement_id,
        lot_id=ligne.lot_remplacement_id,
        emplacement_id=ligne.emplacement_remplacement_id,
        reference_article=ligne.article_remplacement.reference,
        delta=ligne.quantite_remplacement,
    )

    _appliquer_delta(
        db,
        article_id=reservation.article_id,
        lot_id=reservation.lot_id,
        emplacement_id=reservation.emplacement_id,
        reference_article=reservation.article.reference,
        delta=-reservation.quantite,
    )

    reservation.article_id = ligne.article_remplacement_id
    reservation.lot_id = ligne.lot_remplacement_id
    reservation.emplacement_id = ligne.emplacement_remplacement_id
    reservation.quantite = ligne.quantite_remplacement
    reservation.reserve_par = reserve_par
    reservation.motif = (
        f"Remplacement de {ligne.article.reference} — "
        f"{ligne.commentaire_remplacement or preparation.nom}"
    )
    reservation.statut = "ACTIVE"
    reservation.date_liberation = None

    return reservation


def liberer_reservation_ligne(
    db: Session,
    ligne: LignePreparation,
) -> None:
    reservation = _reservation_active(db, ligne.id)
    if reservation is None:
        return

    _appliquer_delta(
        db,
        article_id=reservation.article_id,
        lot_id=reservation.lot_id,
        emplacement_id=reservation.emplacement_id,
        reference_article=reservation.article.reference,
        delta=-reservation.quantite,
    )

    reservation.statut = "LIBEREE"
    reservation.date_liberation = datetime.now(timezone.utc)


def liberer_reservations_preparation(
    db: Session,
    preparation: Preparation,
) -> None:
    for ligne in preparation.lignes:
        liberer_reservation_ligne(db, ligne)
