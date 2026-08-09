from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.alerte import AlerteLogistique
from app.models.utilisateur import Utilisateur
from app.schemas.alerte import AlerteLogistiqueRead, ResumeAlertesRead
from app.services.alertes import synchroniser_alertes


router = APIRouter(prefix="/api/alertes", tags=["Alertes"])


@router.get("", response_model=list[AlerteLogistiqueRead])
def lister_alertes(
    statut: str | None = Query(default=None),
    categorie: str | None = Query(default=None),
    niveau: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> list[AlerteLogistique]:
    synchroniser_alertes(db)
    db.commit()

    requete = select(AlerteLogistique).order_by(
        AlerteLogistique.statut.asc(),
        AlerteLogistique.niveau.asc(),
        AlerteLogistique.date_derniere_detection.desc(),
    )
    if statut:
        requete = requete.where(AlerteLogistique.statut == statut)
    if categorie:
        requete = requete.where(AlerteLogistique.categorie == categorie)
    if niveau:
        requete = requete.where(AlerteLogistique.niveau == niveau)

    return list(db.scalars(requete).all())


@router.get("/resume", response_model=ResumeAlertesRead)
def resume_alertes(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> ResumeAlertesRead:
    synchroniser_alertes(db)
    db.commit()

    actives = db.scalar(
        select(func.count(AlerteLogistique.id)).where(
            AlerteLogistique.statut.in_(["ACTIVE", "ACQUITTEE"])
        )
    ) or 0
    critiques = db.scalar(
        select(func.count(AlerteLogistique.id)).where(
            AlerteLogistique.statut.in_(["ACTIVE", "ACQUITTEE"]),
            AlerteLogistique.niveau == "CRITIQUE",
        )
    ) or 0
    avertissements = db.scalar(
        select(func.count(AlerteLogistique.id)).where(
            AlerteLogistique.statut.in_(["ACTIVE", "ACQUITTEE"]),
            AlerteLogistique.niveau == "AVERTISSEMENT",
        )
    ) or 0
    acquittees = db.scalar(
        select(func.count(AlerteLogistique.id)).where(
            AlerteLogistique.statut == "ACQUITTEE"
        )
    ) or 0

    return ResumeAlertesRead(
        actives=actives,
        critiques=critiques,
        avertissements=avertissements,
        acquittees=acquittees,
    )


@router.patch(
    "/{alerte_id}/acquitter",
    response_model=AlerteLogistiqueRead,
)
def acquitter_alerte(
    alerte_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> AlerteLogistique:
    synchroniser_alertes(db)

    alerte = db.get(AlerteLogistique, alerte_id)
    if alerte is None:
        db.rollback()
        raise HTTPException(status_code=404, detail="Alerte introuvable.")

    if alerte.statut == "RESOLUE":
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cette alerte est déjà résolue.",
        )

    alerte.statut = "ACQUITTEE"
    alerte.acquittee_par = utilisateur.nom_complet
    alerte.date_acquittement = datetime.now(timezone.utc)

    db.commit()
    db.refresh(alerte)
    return alerte


@router.patch(
    "/{alerte_id}/reactiver",
    response_model=AlerteLogistiqueRead,
)
def reactiver_alerte(
    alerte_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> AlerteLogistique:
    synchroniser_alertes(db)

    alerte = db.get(AlerteLogistique, alerte_id)
    if alerte is None:
        db.rollback()
        raise HTTPException(status_code=404, detail="Alerte introuvable.")

    if alerte.statut == "RESOLUE":
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Une alerte résolue ne peut pas être réactivée manuellement.",
        )

    alerte.statut = "ACTIVE"
    alerte.acquittee_par = None
    alerte.date_acquittement = None

    db.commit()
    db.refresh(alerte)
    return alerte
