from sqlalchemy.orm import Session

from app.models.reservation import Notification


def creer_notification(
    db: Session,
    destinataire: str | None,
    titre: str,
    message: str,
    lien: str | None = None,
    type_notification: str = "INFORMATION",
) -> None:
    if not destinataire or not destinataire.strip():
        return

    db.add(
        Notification(
            destinataire=destinataire.strip(),
            titre=titre,
            message=message,
            lien=lien,
            type=type_notification,
        )
    )
