from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import hacher_jeton
from app.db.session import get_db
from app.models.utilisateur import SessionUtilisateur, Utilisateur


def utilisateur_courant(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Utilisateur:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
        )

    jeton = authorization.removeprefix("Bearer ").strip()
    session = db.scalar(
        select(SessionUtilisateur)
        .options(joinedload(SessionUtilisateur.utilisateur))
        .where(
            SessionUtilisateur.jeton_hash == hacher_jeton(jeton),
            SessionUtilisateur.date_revocation.is_(None),
            SessionUtilisateur.date_expiration > datetime.now(timezone.utc),
        )
    )

    if (
        session is None
        or session.utilisateur is None
        or not session.utilisateur.actif
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalide ou expirée.",
        )

    return session.utilisateur


def exiger_roles(*roles: str):
    def dependance(
        utilisateur: Utilisateur = Depends(utilisateur_courant),
    ) -> Utilisateur:
        if utilisateur.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Droits insuffisants.",
            )
        return utilisateur

    return dependance
