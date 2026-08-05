from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.affaire import Affaire
from app.schemas.affaire import AffaireCreate, AffaireRead, AffaireUpdate

router = APIRouter(prefix="/api/affaires", tags=["Affaires"])


@router.get("", response_model=list[AffaireRead])
def lister_affaires(
    recherche: str | None = Query(default=None, max_length=100),
    statut: str | None = None,
    actifs_uniquement: bool = True,
    db: Session = Depends(get_db),
) -> list[Affaire]:
    requete = select(Affaire).order_by(
        Affaire.date_creation.desc(),
        Affaire.reference.desc(),
    )

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                Affaire.reference.ilike(terme),
                Affaire.code_externe.ilike(terme),
                Affaire.nom.ilike(terme),
                Affaire.client.ilike(terme),
                Affaire.site.ilike(terme),
                Affaire.charge_affaires.ilike(terme),
            )
        )

    if statut:
        requete = requete.where(Affaire.statut == statut.upper())

    if actifs_uniquement:
        requete = requete.where(Affaire.actif.is_(True))

    return list(db.scalars(requete).all())


@router.post(
    "",
    response_model=AffaireRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_affaire(
    payload: AffaireCreate,
    db: Session = Depends(get_db),
) -> Affaire:
    affaire = Affaire(**payload.model_dump())
    db.add(affaire)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code d’affaire existe déjà.",
        )

    db.refresh(affaire)
    return affaire


@router.patch("/{affaire_id}", response_model=AffaireRead)
def modifier_affaire(
    affaire_id: int,
    payload: AffaireUpdate,
    db: Session = Depends(get_db),
) -> Affaire:
    affaire = db.get(Affaire, affaire_id)
    if affaire is None:
        raise HTTPException(status_code=404, detail="Affaire introuvable.")

    donnees = payload.model_dump(exclude_unset=True)

    date_debut = donnees.get("date_debut", affaire.date_debut)
    date_fin_prevue = donnees.get(
        "date_fin_prevue",
        affaire.date_fin_prevue,
    )
    if (
        date_debut is not None
        and date_fin_prevue is not None
        and date_fin_prevue < date_debut
    ):
        raise HTTPException(
            status_code=422,
            detail="Les dates de l’affaire sont incohérentes.",
        )

    for champ, valeur in donnees.items():
        setattr(affaire, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code d’affaire existe déjà.",
        )

    db.refresh(affaire)
    return affaire
