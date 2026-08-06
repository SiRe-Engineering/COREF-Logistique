from decimal import Decimal

from fastapi import HTTPException

from app.models.reservation import ReservationStock
from app.models.stock import Stock


def test_stock_disponible_tient_compte_du_reserve() -> None:
    stock = Stock(
        article_id=1,
        emplacement_id=1,
        quantite_physique=Decimal("100"),
        quantite_reservee=Decimal("30"),
    )
    disponible = stock.quantite_physique - stock.quantite_reservee
    assert disponible == Decimal("70")


def test_reservation_active_est_liee_a_une_ligne() -> None:
    reservation = ReservationStock(
        article_id=1,
        emplacement_id=1,
        preparation_id=1,
        ligne_preparation_id=1,
        quantite=Decimal("25"),
        reserve_pour="PREP-000001",
        statut="ACTIVE",
    )
    assert reservation.ligne_preparation_id == 1
    assert reservation.statut == "ACTIVE"
