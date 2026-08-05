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

gestion_utilisateurs_requise = exiger_roles(
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
)


def nom_affiche(payload: UtilisateurCreate) -> str:
    if payload.type_compte == "TECHNIQUE":
        return (payload.nom_complet or "").strip()

    return f"{payload.prenom.strip()} {payload.nom.strip()}"


@router.get("", response_model=list[UtilisateurRead])
def lister_utilisateurs(
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(
        gestion_utilisateurs_requise
    ),
) -> list[Utilisateur]:
    requete = select(Utilisateur).order_by(
        Utilisateur.entreprise,
        Utilisateur.nom_complet,
    )

    # Un administrateur COREF ne voit pas les comptes techniques.
    if administrateur.role == "ADMINISTRATEUR_COREF":
        requete = requete.where(
            Utilisateur.type_compte == "METIER",
            Utilisateur.entreprise == "COREF",
        )

    return list(db.scalars(requete).all())


@router.post(
    "",
    response_model=UtilisateurRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_utilisateur(
    payload: UtilisateurCreate,
    db: Session = Depends(get_db),
    administrateur: Utilisateur = Depends(
        gestion_utilisateurs_requise
    ),
) -> Utilisateur:
    if (
        administrateur.role == "ADMINISTRATEUR_COREF"
        and (
            payload.type_compte != "METIER"
            or payload.entreprise.upper() != "COREF"
            or payload.role == "ADMINISTRATEUR_TECHNIQUE"
        )
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Un administrateur COREF ne peut créer que des comptes "
                "métier COREF."
            ),
        )

    utilisateur = Utilisateur(
        nom_complet=nom_affiche(payload),
        prenom=payload.prenom.strip() if payload.prenom else None,
        nom=payload.nom.strip() if payload.nom else None,
        email=payload.email.lower().strip(),
        mot_de_passe_hash=hacher_mot_de_passe(payload.mot_de_passe),
        role=payload.role,
        type_compte=payload.type_compte,
        entreprise=payload.entreprise.strip(),
        fonction=payload.fonction,
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
    administrateur: Utilisateur = Depends(
        gestion_utilisateurs_requise
    ),
) -> Utilisateur:
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable.",
        )

    if (
        administrateur.role == "ADMINISTRATEUR_COREF"
        and (
            utilisateur.type_compte == "TECHNIQUE"
            or utilisateur.entreprise != "COREF"
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Ce compte est réservé à l’administration technique.",
        )

    donnees = payload.model_dump(exclude_unset=True)
    mot_de_passe = donnees.pop("mot_de_passe", None)

    for champ, valeur in donnees.items():
        if champ == "email" and valeur is not None:
            valeur = valeur.lower().strip()
        setattr(utilisateur, champ, valeur)

    if utilisateur.type_compte == "METIER":
        if utilisateur.prenom and utilisateur.nom:
            utilisateur.nom_complet = (
                f"{utilisateur.prenom.strip()} "
                f"{utilisateur.nom.strip()}"
            )
    elif payload.nom_complet:
        utilisateur.nom_complet = payload.nom_complet.strip()

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
