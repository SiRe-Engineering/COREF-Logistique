from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.emplacement import Emplacement
from app.schemas.emplacement import (
    EmplacementCreate,
    EmplacementRead,
    EmplacementUpdate,
)

router = APIRouter(prefix="/api/emplacements", tags=["Emplacements"], dependencies=[Depends(utilisateur_courant)])


def generer_code(payload: EmplacementCreate) -> str:
    if payload.type.upper() == "CASE_MOULE":
        return (
            f"MOU-{payload.allee}-{payload.rack}-"
            f"E{payload.etage}-{payload.case}"
        ).upper()

    base = "".join(
        caractere
        for caractere in payload.nom.upper().replace(" ", "-")
        if caractere.isalnum() or caractere == "-"
    )
    return base[:40]


@router.get("", response_model=list[EmplacementRead])
def lister_emplacements(
    racines_uniquement: bool = Query(default=True),
    actifs_uniquement: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[Emplacement]:
    requete = (
        select(Emplacement)
        .options(selectinload(Emplacement.enfants))
        .order_by(Emplacement.code)
    )

    if racines_uniquement:
        requete = requete.where(Emplacement.parent_id.is_(None))
    if actifs_uniquement:
        requete = requete.where(Emplacement.actif.is_(True))

    return list(db.scalars(requete).unique().all())


@router.post(
    "",
    response_model=EmplacementRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_emplacement(
    payload: EmplacementCreate,
    db: Session = Depends(get_db),
) -> Emplacement:
    if payload.parent_id is not None and db.get(Emplacement, payload.parent_id) is None:
        raise HTTPException(status_code=404, detail="Emplacement parent introuvable.")

    donnees = payload.model_dump(exclude={"code"})
    emplacement = Emplacement(
        **donnees,
        code=(payload.code or generer_code(payload)).strip().upper(),
        type=payload.type.strip().upper(),
        allee=payload.allee.strip().upper() if payload.allee else None,
        rack=payload.rack.strip().upper() if payload.rack else None,
        case=payload.case.strip().upper() if payload.case else None,
    )
    db.add(emplacement)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce code d’emplacement existe déjà.",
        )

    db.refresh(emplacement)
    return emplacement


@router.patch("/{emplacement_id}", response_model=EmplacementRead)
def modifier_emplacement(
    emplacement_id: int,
    payload: EmplacementUpdate,
    db: Session = Depends(get_db),
) -> Emplacement:
    emplacement = db.get(Emplacement, emplacement_id)
    if emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement introuvable.")

    donnees = payload.model_dump(exclude_unset=True)
    for champ in ("type", "allee", "rack", "case"):
        if donnees.get(champ):
            donnees[champ] = donnees[champ].strip().upper()

    for champ, valeur in donnees.items():
        setattr(emplacement, champ, valeur)

    db.commit()
    db.refresh(emplacement)
    return emplacement


@router.delete("/{emplacement_id}", status_code=status.HTTP_204_NO_CONTENT)
def archiver_emplacement(
    emplacement_id: int,
    db: Session = Depends(get_db),
) -> None:
    emplacement = db.get(Emplacement, emplacement_id)
    if emplacement is None:
        raise HTTPException(status_code=404, detail="Emplacement introuvable.")
    emplacement.actif = False
    db.commit()
