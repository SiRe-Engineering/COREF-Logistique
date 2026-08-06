from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.affaire import Affaire
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.famille import Famille
from app.models.lot_beton import LotBeton, StockLot
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


def _article_est_beton(db: Session, article: Article) -> bool:
    if article.famille_id is None:
        return False
    famille = db.get(Famille, article.famille_id)
    return famille is not None and famille.code == "BET"


def _charger_lot(
    db: Session,
    article: Article,
    lot_id: int | None,
) -> LotBeton | None:
    est_beton = _article_est_beton(db, article)

    if est_beton and lot_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Un lot est obligatoire pour les mouvements de béton.",
        )

    if lot_id is None:
        return None

    lot = db.get(LotBeton, lot_id)
    if lot is None or not lot.actif:
        raise HTTPException(status_code=404, detail="Lot béton introuvable.")

    if lot.article_id != article.id:
        raise HTTPException(
            status_code=422,
            detail="Le lot sélectionné n’appartient pas à cet article.",
        )

    return lot


def _charger_affaire(
    db: Session,
    affaire_id: int | None,
    sortie_libre: bool,
    type_mouvement: str,
) -> Affaire | None:
    if type_mouvement != "SORTIE":
        return db.get(Affaire, affaire_id) if affaire_id else None

    if affaire_id is None:
        if sortie_libre:
            return None
        raise HTTPException(
            status_code=422,
            detail="Une sortie exige une affaire ou le mode sortie libre.",
        )

    affaire = db.get(Affaire, affaire_id)
    if affaire is None or not affaire.actif:
        raise HTTPException(status_code=404, detail="Affaire introuvable.")

    if affaire.statut in {"TERMINEE", "ANNULEE"}:
        raise HTTPException(
            status_code=409,
            detail="Cette affaire n’accepte plus de nouvelles sorties.",
        )

    return affaire


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


def _charger_stock_lot_verrouille(
    db: Session,
    lot_id: int,
    emplacement_id: int,
    creer: bool,
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
        if not creer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce lot n’est pas présent dans l’emplacement source.",
            )
        stock_lot = StockLot(
            lot_id=lot_id,
            emplacement_id=emplacement_id,
            quantite_physique=Decimal("0"),
            quantite_reservee=Decimal("0"),
        )
        db.add(stock_lot)
        db.flush()

    return stock_lot


def _retirer(stock, quantite: Decimal, libelle: str) -> None:
    disponible = stock.quantite_physique - stock.quantite_reservee
    if disponible < quantite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Stock disponible insuffisant {libelle}: "
                f"{disponible} disponible pour {quantite} demandé."
            ),
        )
    stock.quantite_physique -= quantite


def executer_mouvement(
    db: Session,
    payload: MouvementCreate,
) -> MouvementStock:
    article = _charger_article(db, payload.article_id)
    lot = _charger_lot(db, article, payload.lot_id)
    affaire = _charger_affaire(
        db,
        payload.affaire_id,
        payload.sortie_libre,
        payload.type,
    )

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

    donnees = payload.model_dump()
    if affaire is not None:
        if not donnees.get("charge_affaires"):
            donnees["charge_affaires"] = affaire.charge_affaires
        if not donnees.get("zone_intervention"):
            donnees["zone_intervention"] = affaire.zone_intervention

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
                article.id,
                payload.emplacement_destination_id,
                creer=True,
            )
            destination.quantite_physique += quantite

            if lot is not None:
                destination_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    payload.emplacement_destination_id,
                    creer=True,
                )
                destination_lot.quantite_physique += quantite

        elif type_mouvement in {
            "SORTIE",
            "AJUSTEMENT_NEGATIF",
        }:
            source = _charger_stock_verrouille(
                db,
                article.id,
                payload.emplacement_source_id,
                creer=False,
            )
            _retirer(source, quantite, "article")

            if lot is not None:
                source_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    payload.emplacement_source_id,
                    creer=False,
                )
                _retirer(source_lot, quantite, "du lot")

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
                    article.id,
                    emplacement_id,
                    creer=(
                        emplacement_id
                        == payload.emplacement_destination_id
                    ),
                )

            source = stocks[payload.emplacement_source_id]
            destination = stocks[payload.emplacement_destination_id]
            _retirer(source, quantite, "article")
            destination.quantite_physique += quantite

            if lot is not None:
                stocks_lots = {}
                for emplacement_id in ids:
                    stocks_lots[emplacement_id] = (
                        _charger_stock_lot_verrouille(
                            db,
                            lot.id,
                            emplacement_id,
                            creer=(
                                emplacement_id
                                == payload.emplacement_destination_id
                            ),
                        )
                    )

                source_lot = stocks_lots[payload.emplacement_source_id]
                destination_lot = stocks_lots[
                    payload.emplacement_destination_id
                ]
                _retirer(source_lot, quantite, "du lot")
                destination_lot.quantite_physique += quantite

        mouvement = MouvementStock(**donnees)
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



def annuler_mouvement(
    db: Session,
    mouvement: MouvementStock,
    *,
    annule_par: str,
    motif: str,
) -> MouvementStock:
    if mouvement.annule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette écriture est déjà annulée.",
        )

    article = _charger_article(db, mouvement.article_id)
    lot = (
        db.get(LotBeton, mouvement.lot_id)
        if mouvement.lot_id is not None
        else None
    )
    quantite = mouvement.quantite

    try:
        if mouvement.type in {
            "ENTREE",
            "RETOUR",
            "AJUSTEMENT_POSITIF",
        }:
            destination = _charger_stock_verrouille(
                db,
                article.id,
                mouvement.emplacement_destination_id,
                creer=False,
            )
            _retirer(destination, quantite, "article")

            if lot is not None:
                destination_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    mouvement.emplacement_destination_id,
                    creer=False,
                )
                _retirer(destination_lot, quantite, "du lot")

        elif mouvement.type in {
            "SORTIE",
            "AJUSTEMENT_NEGATIF",
        }:
            source = _charger_stock_verrouille(
                db,
                article.id,
                mouvement.emplacement_source_id,
                creer=True,
            )
            source.quantite_physique += quantite

            if lot is not None:
                source_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    mouvement.emplacement_source_id,
                    creer=True,
                )
                source_lot.quantite_physique += quantite

        elif mouvement.type == "TRANSFERT":
            destination = _charger_stock_verrouille(
                db,
                article.id,
                mouvement.emplacement_destination_id,
                creer=False,
            )
            _retirer(destination, quantite, "article destination")

            source = _charger_stock_verrouille(
                db,
                article.id,
                mouvement.emplacement_source_id,
                creer=True,
            )
            source.quantite_physique += quantite

            if lot is not None:
                destination_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    mouvement.emplacement_destination_id,
                    creer=False,
                )
                _retirer(
                    destination_lot,
                    quantite,
                    "du lot destination",
                )

                source_lot = _charger_stock_lot_verrouille(
                    db,
                    lot.id,
                    mouvement.emplacement_source_id,
                    creer=True,
                )
                source_lot.quantite_physique += quantite
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Type de mouvement non annulable.",
            )

        mouvement.annule = True
        mouvement.date_annulation = datetime.now(timezone.utc)
        mouvement.annule_par = annule_par
        mouvement.motif_annulation = motif.strip()

        db.commit()
        db.refresh(mouvement)
        return mouvement
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
