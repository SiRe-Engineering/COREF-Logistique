from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    generer_jeton,
    hacher_jeton,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.utilisateur import SessionUtilisateur, Utilisateur
from app.schemas.utilisateur import (
    LoginRequest,
    LoginResponse,
    UtilisateurRead,
)

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


COMPTES_INITIAUX = {
    "contact@sire-engineering.fr": "Sire-2026!",
    "simon.goubet@coref.fr": "Coref-2026!",
}


def initialiser_comptes(db: Session) -> None:
    comptes = list(
        db.scalars(
            select(Utilisateur).where(
                Utilisateur.email.in_(COMPTES_INITIAUX)
            )
        ).all()
    )

    modification = False
    for utilisateur in comptes:
        if utilisateur.mot_de_passe_hash == "INITIALISATION_REQUISE":
            utilisateur.mot_de_passe_hash = hacher_mot_de_passe(
                COMPTES_INITIAUX[utilisateur.email]
            )
            modification = True

    if modification:
        db.commit()


@router.post("/login", response_model=LoginResponse)
def connexion(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    initialiser_comptes(db)

    utilisateur = db.scalar(
        select(Utilisateur).where(
            Utilisateur.email == payload.email.lower().strip()
        )
    )
    if (
        utilisateur is None
        or not utilisateur.actif
        or not verifier_mot_de_passe(
            payload.mot_de_passe,
            utilisateur.mot_de_passe_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects.",
        )

    jeton = generer_jeton()
    db.add(
        SessionUtilisateur(
            utilisateur_id=utilisateur.id,
            jeton_hash=hacher_jeton(jeton),
            date_expiration=(
                datetime.now(timezone.utc) + timedelta(hours=12)
            ),
        )
    )
    db.commit()

    return LoginResponse(
        jeton=jeton,
        utilisateur=utilisateur,
    )


@router.get("/me", response_model=UtilisateurRead)
def lire_session(
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Utilisateur:
    return utilisateur


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def deconnexion(
    utilisateur: Utilisateur = Depends(utilisateur_courant),
    db: Session = Depends(get_db),
) -> None:
    maintenant = datetime.now(timezone.utc)
    sessions = db.scalars(
        select(SessionUtilisateur).where(
            SessionUtilisateur.utilisateur_id == utilisateur.id,
            SessionUtilisateur.date_revocation.is_(None),
        )
    ).all()

    for session in sessions:
        session.date_revocation = maintenant

    db.commit()
