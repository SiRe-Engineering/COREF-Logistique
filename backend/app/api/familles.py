from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.famille import Famille, SousFamille
from app.schemas.famille import (
    FamilleCreate,
    FamilleRead,
    FamilleUpdate,
    SousFamilleCreate,
    SousFamilleRead,
    SousFamilleUpdate,
)

router = APIRouter(prefix="/api", tags=["Familles"], dependencies=[Depends(utilisateur_courant)])


def lever_conflit(db: Session) -> None:
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Le code ou le nom existe déjà dans ce référentiel.",
    )


@router.get("/familles", response_model=list[FamilleRead])
def lister_familles(
    actifs_uniquement: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[Famille]:
    requete = (
        select(Famille)
        .options(selectinload(Famille.sous_familles))
        .order_by(Famille.nom)
    )
    if actifs_uniquement:
        requete = requete.where(Famille.actif.is_(True))

    familles = list(db.scalars(requete).unique().all())
    if actifs_uniquement:
        for famille in familles:
            famille.sous_familles = [
                sf for sf in famille.sous_familles if sf.actif
            ]
    return familles


@router.get("/sous-familles", response_model=list[SousFamilleRead])
def lister_sous_familles(
    famille_id: int | None = None,
    actifs_uniquement: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> list[SousFamille]:
    requete = select(SousFamille).order_by(SousFamille.nom)
    if famille_id is not None:
        requete = requete.where(SousFamille.famille_id == famille_id)
    if actifs_uniquement:
        requete = requete.where(SousFamille.actif.is_(True))
    return list(db.scalars(requete).all())


@router.post("/familles", response_model=FamilleRead, status_code=status.HTTP_201_CREATED)
def creer_famille(payload: FamilleCreate, db: Session = Depends(get_db)) -> Famille:
    famille = Famille(**payload.model_dump())
    db.add(famille)
    try:
        db.commit()
    except IntegrityError:
        lever_conflit(db)
    db.refresh(famille)
    return famille


@router.patch("/familles/{famille_id}", response_model=FamilleRead)
def modifier_famille(
    famille_id: int,
    payload: FamilleUpdate,
    db: Session = Depends(get_db),
) -> Famille:
    famille = db.get(Famille, famille_id)
    if famille is None:
        raise HTTPException(status_code=404, detail="Famille introuvable.")

    donnees = payload.model_dump(exclude_unset=True)
    if donnees.get("code"):
        donnees["code"] = donnees["code"].strip().upper()
    if donnees.get("nom"):
        donnees["nom"] = donnees["nom"].strip()

    for champ, valeur in donnees.items():
        setattr(famille, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        lever_conflit(db)
    db.refresh(famille)
    return famille


@router.delete("/familles/{famille_id}", status_code=status.HTTP_204_NO_CONTENT)
def archiver_famille(famille_id: int, db: Session = Depends(get_db)) -> None:
    famille = db.get(Famille, famille_id)
    if famille is None:
        raise HTTPException(status_code=404, detail="Famille introuvable.")
    famille.actif = False
    db.commit()


@router.post(
    "/sous-familles",
    response_model=SousFamilleRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_sous_famille(
    payload: SousFamilleCreate,
    db: Session = Depends(get_db),
) -> SousFamille:
    if db.get(Famille, payload.famille_id) is None:
        raise HTTPException(status_code=404, detail="Famille introuvable.")

    sous_famille = SousFamille(**payload.model_dump())
    db.add(sous_famille)
    try:
        db.commit()
    except IntegrityError:
        lever_conflit(db)
    db.refresh(sous_famille)
    return sous_famille


@router.patch("/sous-familles/{sous_famille_id}", response_model=SousFamilleRead)
def modifier_sous_famille(
    sous_famille_id: int,
    payload: SousFamilleUpdate,
    db: Session = Depends(get_db),
) -> SousFamille:
    sous_famille = db.get(SousFamille, sous_famille_id)
    if sous_famille is None:
        raise HTTPException(status_code=404, detail="Sous-famille introuvable.")

    donnees = payload.model_dump(exclude_unset=True)
    if donnees.get("code"):
        donnees["code"] = donnees["code"].strip().upper()
    if donnees.get("nom"):
        donnees["nom"] = donnees["nom"].strip()

    for champ, valeur in donnees.items():
        setattr(sous_famille, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        lever_conflit(db)
    db.refresh(sous_famille)
    return sous_famille


@router.delete("/sous-familles/{sous_famille_id}", status_code=status.HTTP_204_NO_CONTENT)
def archiver_sous_famille(
    sous_famille_id: int,
    db: Session = Depends(get_db),
) -> None:
    sous_famille = db.get(SousFamille, sous_famille_id)
    if sous_famille is None:
        raise HTTPException(status_code=404, detail="Sous-famille introuvable.")
    sous_famille.actif = False
    db.commit()
