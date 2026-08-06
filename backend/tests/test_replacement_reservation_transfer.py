from decimal import Decimal

from app.models.reservation import ReservationStock


def test_reservation_change_de_cible() -> None:
    reservation = ReservationStock(
        article_id=1,
        lot_id=None,
        emplacement_id=1,
        preparation_id=1,
        ligne_preparation_id=1,
        quantite=Decimal("100"),
        reserve_pour="PREP-000001",
        statut="ACTIVE",
    )

    reservation.article_id = 2
    reservation.emplacement_id = 3
    reservation.quantite = Decimal("80")

    assert reservation.article_id == 2
    assert reservation.emplacement_id == 3
    assert reservation.quantite == Decimal("80")
