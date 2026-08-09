from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.reservation import Notification, ReservationStock
from app.models.utilisateur import Utilisateur
from app.schemas.reservation import NotificationRead, ReservationRead

router_reservations = APIRouter(
    prefix="/api/reservations",
    tags=["Réservations"],
)
router_notifications = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router_reservations.get("", response_model=list[ReservationRead])
def lister_reservations(
    article_id: int | None = None,
    emplacement_id: int | None = None,
    preparation_id: int | None = None,
    actives_uniquement: bool = True,
    db: Session = Depends(get_db),
) -> list[ReservationStock]:
    requete = (
        select(ReservationStock)
        .options(
            joinedload(ReservationStock.article),
            joinedload(ReservationStock.lot),
            joinedload(ReservationStock.emplacement),
            joinedload(ReservationStock.preparation),
        )
        .order_by(ReservationStock.date_creation.desc())
    )

    if article_id is not None:
        requete = requete.where(
            ReservationStock.article_id == article_id
        )
    if emplacement_id is not None:
        requete = requete.where(
            ReservationStock.emplacement_id == emplacement_id
        )
    if preparation_id is not None:
        requete = requete.where(
            ReservationStock.preparation_id == preparation_id
        )
    if actives_uniquement:
        requete = requete.where(
            ReservationStock.statut == "ACTIVE"
        )

    return list(db.scalars(requete).unique().all())


@router_notifications.get("/me", response_model=list[NotificationRead])
def mes_notifications(
    non_lues_uniquement: bool = False,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> list[Notification]:
    requete = (
        select(Notification)
        .where(
            Notification.destinataire.ilike(
                utilisateur.nom_complet.strip()
            )
        )
        .order_by(Notification.date_creation.desc())
        .limit(100)
    )

    if non_lues_uniquement:
        requete = requete.where(Notification.lue.is_(False))

    return list(db.scalars(requete).all())


@router_notifications.patch(
    "/{notification_id}/lire",
    response_model=NotificationRead,
)
def marquer_lue(
    notification_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification introuvable.",
        )

    if (
        notification.destinataire.strip().lower()
        != utilisateur.nom_complet.strip().lower()
    ):
        raise HTTPException(
            status_code=403,
            detail="Cette notification ne vous appartient pas.",
        )

    notification.lue = True
    notification.date_lecture = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification
