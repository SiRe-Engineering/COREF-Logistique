from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.affaire import Affaire
from app.models.emplacement import Emplacement
from app.models.materiel import Materiel
from app.schemas.materiel import MaterielCreate, MaterielRead, MaterielUpdate

router = APIRouter(prefix="/api/materiels", tags=["Matériels"])


def verifier_relations(
    db: Session,
    emplacement_id: int | None,
    affaire_id: int | None,
) -> None:
    if emplacement_id is not None:
        emplacement = db.get(Emplacement, emplacement_id)
        if emplacement is None or not emplacement.actif:
            raise HTTPException(
                status_code=404,
                detail="Emplacement introuvable.",
            )

    if affaire_id is not None:
        affaire = db.get(Affaire, affaire_id)
        if affaire is None or not affaire.actif:
            raise HTTPException(
                status_code=404,
                detail="Affaire introuvable.",
            )
        if affaire.statut in {"TERMINEE", "ANNULEE"}:
            raise HTTPException(
                status_code=409,
                detail="Cette affaire ne peut plus recevoir de matériel.",
            )


@router.get("", response_model=list[MaterielRead])
def lister_materiels(
    recherche: str | None = Query(default=None, max_length=100),
    categorie: str | None = None,
    etat: str | None = None,
    controles_a_venir: bool = False,
    actifs_uniquement: bool = True,
    db: Session = Depends(get_db),
) -> list[Materiel]:
    requete = (
        select(Materiel)
        .options(
            joinedload(Materiel.emplacement),
            joinedload(Materiel.affaire),
        )
        .order_by(Materiel.numero_inventaire)
    )

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                Materiel.numero_inventaire.ilike(terme),
                Materiel.designation.ilike(terme),
                Materiel.marque.ilike(terme),
                Materiel.modele.ilike(terme),
                Materiel.numero_serie.ilike(terme),
            )
        )

    if categorie:
        requete = requete.where(
            Materiel.categorie == categorie
        )

    if etat:
        requete = requete.where(Materiel.etat == etat.upper())

    if controles_a_venir:
        limite = date.today() + timedelta(days=30)
        requete = requete.where(
            Materiel.date_prochain_controle.is_not(None),
            Materiel.date_prochain_controle <= limite,
        )

    if actifs_uniquement:
        requete = requete.where(Materiel.actif.is_(True))

    return list(db.scalars(requete).unique().all())


@router.post(
    "",
    response_model=MaterielRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_materiel(
    payload: MaterielCreate,
    db: Session = Depends(get_db),
) -> Materiel:
    verifier_relations(
        db,
        payload.emplacement_id,
        payload.affaire_id,
    )

    materiel = Materiel(**payload.model_dump())
    db.add(materiel)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce numéro de série existe déjà.",
        )

    db.refresh(materiel)
    return materiel


@router.patch("/{materiel_id}", response_model=MaterielRead)
def modifier_materiel(
    materiel_id: int,
    payload: MaterielUpdate,
    db: Session = Depends(get_db),
) -> Materiel:
    materiel = db.get(Materiel, materiel_id)
    if materiel is None:
        raise HTTPException(status_code=404, detail="Matériel introuvable.")

    donnees = payload.model_dump(exclude_unset=True)

    emplacement_id = donnees.get(
        "emplacement_id",
        materiel.emplacement_id,
    )
    affaire_id = donnees.get(
        "affaire_id",
        materiel.affaire_id,
    )
    verifier_relations(db, emplacement_id, affaire_id)

    date_dernier_controle = donnees.get(
        "date_dernier_controle",
        materiel.date_dernier_controle,
    )
    date_prochain_controle = donnees.get(
        "date_prochain_controle",
        materiel.date_prochain_controle,
    )

    if (
        date_dernier_controle is not None
        and date_prochain_controle is not None
        and date_prochain_controle < date_dernier_controle
    ):
        raise HTTPException(
            status_code=422,
            detail="Les dates de contrôle sont incohérentes.",
        )

    etat = donnees.get("etat", materiel.etat)
    if etat == "EN_CHANTIER" and affaire_id is None:
        raise HTTPException(
            status_code=422,
            detail="Un matériel en chantier doit être affecté à une affaire.",
        )

    for champ, valeur in donnees.items():
        setattr(materiel, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce numéro de série existe déjà.",
        )

    db.refresh(materiel)
    return materiel
