from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import exiger_roles, utilisateur_courant
from app.models.affaire import Affaire
from app.models.mouvement import MouvementStock
from app.models.preparation import Preparation
from app.models.utilisateur import Utilisateur
from app.schemas.affaire import AffaireCreate, AffaireRead, AffaireUpdate

router = APIRouter(prefix="/api/affaires", tags=["Affaires"], dependencies=[Depends(utilisateur_courant)])


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



@router.delete("/{affaire_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_affaire(
    affaire_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        exiger_roles("ADMINISTRATEUR_TECHNIQUE")
    ),
) -> None:
    affaire = db.scalar(
        select(Affaire)
        .where(Affaire.id == affaire_id)
        .with_for_update(of=Affaire)
    )
    if affaire is None:
        raise HTTPException(status_code=404, detail="Affaire introuvable.")

    nb_preparations = db.scalar(
        select(func.count(Preparation.id)).where(
            Preparation.affaire_id == affaire.id
        )
    )
    if nb_preparations:
        raise HTTPException(
            status_code=409,
            detail=f"Cette affaire possède encore {nb_preparations} préparation(s).",
        )

    nb_mouvements = db.scalar(
        select(func.count(MouvementStock.id)).where(
            MouvementStock.affaire_id == affaire.id,
            MouvementStock.annule.is_(False),
        )
    )
    if nb_mouvements:
        raise HTTPException(
            status_code=409,
            detail=f"Cette affaire possède encore {nb_mouvements} écriture(s) active(s).",
        )

    try:
        db.delete(affaire)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cette affaire est encore référencée par d’autres données.",
        )
