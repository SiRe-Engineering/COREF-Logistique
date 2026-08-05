from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hacher_mot_de_passe
from app.db.session import get_db
from app.dependencies import exiger_roles
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurRead,
    UtilisateurUpdate,
)

router = APIRouter(prefix="/api/utilisateurs", tags=["Utilisateurs"])

administrateur_requis = exiger_roles("ADMINISTRATEUR")


@router.get("", response_model=list[UtilisateurRead])
def lister_utilisateurs(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(administrateur_requis),
) -> list[Utilisateur]:
    return list(
        db.scalars(
            select(Utilisateur).order_by(Utilisateur.nom_complet)
        ).all()
    )


@router.post(
    "",
    response_model=UtilisateurRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_utilisateur(
    payload: UtilisateurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(administrateur_requis),
) -> Utilisateur:
    utilisateur = Utilisateur(
        nom_complet=payload.nom_complet.strip(),
        email=payload.email.lower().strip(),
        mot_de_passe_hash=hacher_mot_de_passe(payload.mot_de_passe),
        role=payload.role,
    )
    db.add(utilisateur)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cette adresse e-mail existe déjà.",
        )

    db.refresh(utilisateur)
    return utilisateur


@router.patch("/{utilisateur_id}", response_model=UtilisateurRead)
def modifier_utilisateur(
    utilisateur_id: int,
    payload: UtilisateurUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(administrateur_requis),
) -> Utilisateur:
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable.",
        )

    donnees = payload.model_dump(exclude_unset=True)
    mot_de_passe = donnees.pop("mot_de_passe", None)

    for champ, valeur in donnees.items():
        if champ == "email" and valeur is not None:
            valeur = valeur.lower().strip()
        setattr(utilisateur, champ, valeur)

    if mot_de_passe:
        utilisateur.mot_de_passe_hash = hacher_mot_de_passe(
            mot_de_passe
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cette adresse e-mail existe déjà.",
        )

    db.refresh(utilisateur)
    return utilisateur
