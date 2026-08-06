from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies import exiger_roles, utilisateur_courant
from app.models.affaire import Affaire
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.famille import Famille
from app.models.lot_beton import LotBeton
from app.models.preparation import LignePreparation, Preparation
from app.models.reservation import Notification
from app.models.utilisateur import Utilisateur
from app.schemas.mouvement import MouvementCreate
from app.schemas.preparation import (
    DecisionRemplacementCreate,
    LignePreparationCreate,
    PropositionRemplacementCreate,
    LignePreparationUpdate,
    PreparationCreate,
    PreparationRead,
    PreparationUpdate,
)
from app.services.mouvements import executer_mouvement
from app.services.notifications import creer_notification
from app.services.reservations import (
    liberer_reservation_ligne,
    liberer_reservations_preparation,
    synchroniser_reservation_ligne,
    transferer_reservation_remplacement,
)

router = APIRouter(prefix="/api/preparations", tags=["Préparations"])

STATUTS_EDITABLES = {"BROUILLON"}
STATUTS_LIGNE_AUTORISES = {
    "A_PREPARER",
    "PREPAREE",
    "PARTIELLE",
    "INDISPONIBLE",
    "REMPLACEMENT_PROPOSE",
    "REMPLACEMENT_ACCEPTE",
    "REMPLACEMENT_REFUSE",
    "EXPEDIEE",
}


def recalculer_ligne(ligne: LignePreparation) -> None:
    ligne.quantite_manquante = max(
        ligne.quantite_demandee - ligne.quantite_preparee,
        Decimal("0"),
    )

    if ligne.statut in {
        "REMPLACEMENT_PROPOSE",
        "REMPLACEMENT_ACCEPTE",
        "REMPLACEMENT_REFUSE",
        "EXPEDIEE",
    }:
        return

    if ligne.quantite_preparee >= ligne.quantite_demandee:
        ligne.statut = "PREPAREE"
        ligne.quantite_preparee = ligne.quantite_demandee
        ligne.quantite_manquante = Decimal("0")
        ligne.motif_ecart = None
        ligne.date_fin_preparation = datetime.now(timezone.utc)
    elif ligne.quantite_preparee > 0:
        ligne.statut = "PARTIELLE"
        ligne.date_fin_preparation = None
    elif ligne.statut != "INDISPONIBLE":
        ligne.statut = "A_PREPARER"
        ligne.date_fin_preparation = None




def charger_preparation(db: Session, preparation_id: int) -> Preparation:
    preparation = db.scalar(
        select(Preparation)
        .options(selectinload(Preparation.lignes))
        .where(Preparation.id == preparation_id)
    )
    if preparation is None:
        raise HTTPException(status_code=404, detail="Préparation introuvable.")
    return preparation


def article_est_beton(db: Session, article: Article) -> bool:
    if article.famille_id is None:
        return False
    famille = db.get(Famille, article.famille_id)
    return famille is not None and famille.code == "BET"


def notifier_acteurs(
    db: Session,
    preparation: Preparation,
    titre: str,
    message: str,
) -> None:
    lien = f"/preparations?preparation={preparation.id}"
    creer_notification(
        db,
        preparation.demandeur,
        titre,
        message,
        lien,
    )
    if (
        preparation.preparateur
        and preparation.preparateur.strip().lower()
        != (preparation.demandeur or "").strip().lower()
    ):
        creer_notification(
            db,
            preparation.preparateur,
            titre,
            message,
            lien,
        )


@router.get("", response_model=list[PreparationRead])
def lister_preparations(db: Session = Depends(get_db)) -> list[Preparation]:
    return list(
        db.scalars(
            select(Preparation)
            .options(selectinload(Preparation.lignes))
            .order_by(Preparation.date_creation.desc())
        ).unique().all()
    )


@router.get("/{preparation_id}", response_model=PreparationRead)
def lire_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
) -> Preparation:
    return charger_preparation(db, preparation_id)


@router.post(
    "",
    response_model=PreparationRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_preparation(
    payload: PreparationCreate,
    db: Session = Depends(get_db),
) -> Preparation:
    affaire = db.get(Affaire, payload.affaire_id)
    if affaire is None or not affaire.actif:
        raise HTTPException(status_code=404, detail="Affaire introuvable.")
    if affaire.statut in {"TERMINEE", "ANNULEE"}:
        raise HTTPException(
            status_code=409,
            detail="Cette affaire ne peut pas recevoir de préparation.",
        )

    preparation = Preparation(**payload.model_dump(), statut="BROUILLON")
    db.add(preparation)
    db.flush()

    notifier_acteurs(
        db,
        preparation,
        "Nouvelle préparation créée",
        (
            f"{preparation.reference} a été créée pour l’affaire "
            f"{affaire.code_externe or affaire.reference}."
        ),
    )

    db.commit()
    db.refresh(preparation)
    return preparation


@router.patch("/{preparation_id}", response_model=PreparationRead)
def modifier_preparation(
    preparation_id: int,
    payload: PreparationUpdate,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    if preparation.statut not in STATUTS_EDITABLES:
        raise HTTPException(
            status_code=409,
            detail="Cette préparation ne peut plus être modifiée.",
        )

    ancien_demandeur = preparation.demandeur
    ancien_preparateur = preparation.preparateur

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(preparation, champ, valeur)

    if preparation.demandeur != ancien_demandeur:
        creer_notification(
            db,
            preparation.demandeur,
            "Préparation attribuée",
            f"Vous êtes demandeur de {preparation.reference}.",
            f"/preparations?preparation={preparation.id}",
        )
    if preparation.preparateur != ancien_preparateur:
        creer_notification(
            db,
            preparation.preparateur,
            "Préparation à réaliser",
            f"Vous êtes désigné préparateur de {preparation.reference}.",
            f"/preparations?preparation={preparation.id}",
            "ACTION",
        )

    db.commit()
    return charger_preparation(db, preparation_id)


@router.post(
    "/{preparation_id}/lignes",
    response_model=PreparationRead,
    status_code=status.HTTP_201_CREATED,
)
def ajouter_ligne(
    preparation_id: int,
    payload: LignePreparationCreate,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    if preparation.statut not in STATUTS_EDITABLES:
        raise HTTPException(
            status_code=409,
            detail="Cette préparation ne peut plus être modifiée.",
        )

    article = db.get(Article, payload.article_id)
    if article is None or not article.actif:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    if article_est_beton(db, article) and payload.lot_id is None:
        raise HTTPException(
            status_code=422,
            detail="Un lot est obligatoire pour un béton.",
        )

    if payload.lot_id is not None:
        lot = db.get(LotBeton, payload.lot_id)
        if lot is None or lot.article_id != article.id:
            raise HTTPException(
                status_code=422,
                detail="Le lot ne correspond pas à l’article.",
            )

    if payload.emplacement_source_id is not None:
        emplacement = db.get(Emplacement, payload.emplacement_source_id)
        if emplacement is None or not emplacement.actif:
            raise HTTPException(
                status_code=404,
                detail="Emplacement source introuvable.",
            )

    ligne = LignePreparation(
        **payload.model_dump(),
        quantite_preparee=Decimal("0"),
        quantite_manquante=payload.quantite_demandee,
        statut="A_PREPARER",
    )
    preparation.lignes.append(ligne)
    db.flush()

    notifier_acteurs(
        db,
        preparation,
        "Préparation modifiée",
        f"Une ligne a été ajoutée à {preparation.reference}.",
    )
    db.commit()
    return charger_preparation(db, preparation_id)


@router.patch(
    "/{preparation_id}/lignes/{ligne_id}",
    response_model=PreparationRead,
)
def modifier_ligne(
    preparation_id: int,
    ligne_id: int,
    payload: LignePreparationUpdate,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    donnees = payload.model_dump(exclude_unset=True)

    champs_execution = {
        "quantite_preparee",
        "statut",
        "motif_ecart",
    }
    modification_execution = (
        preparation.statut == "EN_PREPARATION"
        and set(donnees).issubset(champs_execution)
    )

    if (
        preparation.statut not in STATUTS_EDITABLES
        and not modification_execution
    ):
        raise HTTPException(
            status_code=409,
            detail="Cette préparation ne peut plus être modifiée.",
        )

    ligne = next(
        (element for element in preparation.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")

    statut_demande = donnees.get("statut")
    if (
        statut_demande is not None
        and statut_demande not in STATUTS_LIGNE_AUTORISES
    ):
        raise HTTPException(
            status_code=422,
            detail="Statut de ligne de préparation invalide.",
        )

    for champ, valeur in donnees.items():
        setattr(ligne, champ, valeur)

    if (
        "quantite_preparee" in donnees
        or "quantite_demandee" in donnees
        or "statut" in donnees
    ):
        if (
            ligne.quantite_preparee > 0
            and ligne.date_debut_preparation is None
        ):
            ligne.date_debut_preparation = datetime.now(timezone.utc)

        if ligne.statut == "INDISPONIBLE":
            ligne.quantite_preparee = Decimal("0")
            ligne.quantite_manquante = ligne.quantite_demandee
            ligne.date_fin_preparation = None
        else:
            recalculer_ligne(ligne)

    if (
        ligne.statut in {"PARTIELLE", "INDISPONIBLE"}
        and not (ligne.motif_ecart or "").strip()
    ):
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=(
                "Un motif est obligatoire pour une ligne "
                "partielle ou indisponible."
            ),
        )

    if ligne.statut in {"A_PREPARER", "PREPAREE"}:
        ligne.motif_ecart = None

    if ligne.lot_id is not None:
        lot = db.get(LotBeton, ligne.lot_id)
        if lot is None or lot.article_id != ligne.article_id:
            raise HTTPException(
                status_code=422,
                detail="Le lot ne correspond pas à l’article.",
            )

    if modification_execution:
        if all(
            element.statut == "PREPAREE"
            for element in preparation.lignes
        ):
            preparation.statut = "PRETE"

    notifier_acteurs(
        db,
        preparation,
        "Préparation modifiée",
        f"Les besoins de {preparation.reference} ont été modifiés.",
    )
    db.commit()
    return charger_preparation(db, preparation_id)


@router.delete(
    "/{preparation_id}/lignes/{ligne_id}",
    response_model=PreparationRead,
)
def supprimer_ligne(
    preparation_id: int,
    ligne_id: int,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    if preparation.statut not in STATUTS_EDITABLES:
        raise HTTPException(
            status_code=409,
            detail="Cette préparation ne peut plus être modifiée.",
        )

    ligne = next(
        (element for element in preparation.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")

    liberer_reservation_ligne(db, ligne)
    preparation.lignes.remove(ligne)

    notifier_acteurs(
        db,
        preparation,
        "Préparation modifiée",
        f"Une ligne a été supprimée de {preparation.reference}.",
    )
    db.commit()
    return charger_preparation(db, preparation_id)


@router.delete(
    "/{preparation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def supprimer_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        exiger_roles("ADMINISTRATEUR_TECHNIQUE")
    ),
) -> None:
    preparation = charger_preparation(db, preparation_id)

    try:
        liberer_reservations_preparation(db, preparation)

        lien = f"/preparations?preparation={preparation.id}"
        for notification in db.scalars(
            select(Notification).where(Notification.lien == lien)
        ).all():
            db.delete(notification)

        db.delete(preparation)
        db.commit()
    except HTTPException:
        db.rollback()
        raise


@router.post("/{preparation_id}/valider", response_model=PreparationRead)
def valider_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)

    if preparation.statut != "BROUILLON":
        raise HTTPException(
            status_code=409,
            detail="Seul un brouillon peut être validé.",
        )
    if not preparation.lignes:
        raise HTTPException(
            status_code=422,
            detail="La préparation ne contient aucune ligne.",
        )

    try:
        for ligne in preparation.lignes:
            synchroniser_reservation_ligne(db, preparation, ligne)
            ligne.statut = "A_PREPARER"
            ligne.quantite_preparee = Decimal("0")
            ligne.quantite_manquante = ligne.quantite_demandee
            ligne.motif_ecart = None

        preparation.statut = "VALIDEE"
        preparation.date_validation = datetime.now(timezone.utc)

        notifier_acteurs(
            db,
            preparation,
            "Stock réservé",
            (
                f"Les matériaux de {preparation.reference} sont réservés. "
                "La préparation peut être démarrée."
            ),
        )
        db.commit()
        return charger_preparation(db, preparation_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


@router.post("/{preparation_id}/demarrer", response_model=PreparationRead)
def demarrer_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    if preparation.statut != "VALIDEE":
        raise HTTPException(
            status_code=409,
            detail="La préparation doit d’abord être validée.",
        )

    preparation.statut = "EN_PREPARATION"
    maintenant = datetime.now(timezone.utc)
    for ligne in preparation.lignes:
        ligne.quantite_preparee = Decimal("0")
        ligne.quantite_manquante = ligne.quantite_demandee
        ligne.statut = "A_PREPARER"
        ligne.motif_ecart = None
        ligne.date_debut_preparation = maintenant
        ligne.date_fin_preparation = None

    notifier_acteurs(
        db,
        preparation,
        "Préparation démarrée",
        f"{preparation.reference} est maintenant en préparation.",
    )
    db.commit()
    return charger_preparation(db, preparation_id)


@router.post("/{preparation_id}/terminer", response_model=PreparationRead)
def terminer_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    if preparation.statut != "EN_PREPARATION":
        raise HTTPException(
            status_code=409,
            detail="La préparation n’est pas en cours.",
        )

    incompletes = [
        ligne
        for ligne in preparation.lignes
        if ligne.statut != "PREPAREE"
    ]
    if incompletes:
        raise HTTPException(
            status_code=422,
            detail="Toutes les quantités demandées doivent être préparées.",
        )

    preparation.statut = "PRETE"
    for ligne in preparation.lignes:
        ligne.statut = "PREPAREE"

    notifier_acteurs(
        db,
        preparation,
        "Préparation prête",
        f"{preparation.reference} est prête à être expédiée.",
    )
    db.commit()
    return charger_preparation(db, preparation_id)


@router.post(
    "/{preparation_id}/expedier",
    response_model=PreparationRead,
)
def expedier_preparation(
    preparation_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)

    if preparation.statut == "EXPEDIEE":
        raise HTTPException(
            status_code=409,
            detail="Cette préparation a déjà été expédiée.",
        )

    if preparation.statut != "PRETE":
        raise HTTPException(
            status_code=409,
            detail="La préparation doit être prête avant expédition.",
        )

    if not preparation.lignes:
        raise HTTPException(
            status_code=422,
            detail="Une préparation vide ne peut pas être expédiée.",
        )

    lignes_non_pretes = [
        ligne
        for ligne in preparation.lignes
        if ligne.statut != "PREPAREE"
        or ligne.quantite_preparee <= Decimal("0")
    ]
    if lignes_non_pretes:
        raise HTTPException(
            status_code=409,
            detail=(
                "Toutes les lignes doivent être entièrement préparées "
                "avant l’expédition."
            ),
        )

    try:
        # La libération et toutes les sorties appartiennent à la même
        # transaction. Aucun commit intermédiaire n'est autorisé.
        liberer_reservations_preparation(db, preparation)

        for ligne in preparation.lignes:
            remplacement_accepte = (
                ligne.decision_remplacement == "ACCEPTEE"
                and ligne.article_remplacement_id is not None
            )

            article_sorti_id = (
                ligne.article_remplacement_id
                if remplacement_accepte
                else ligne.article_id
            )
            lot_sorti_id = (
                ligne.lot_remplacement_id
                if remplacement_accepte
                else ligne.lot_id
            )
            emplacement_sortie_id = (
                ligne.emplacement_remplacement_id
                if remplacement_accepte
                else ligne.emplacement_source_id
            )

            # La quantité sortie est toujours la quantité physiquement
            # préparée. Le besoin initial reste conservé pour la traçabilité.
            quantite_sortie = ligne.quantite_preparee

            if emplacement_sortie_id is None:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"{ligne.article.reference} : "
                        "emplacement source manquant."
                    ),
                )

            commentaire_sortie = ligne.commentaire
            if remplacement_accepte:
                commentaire_sortie = (
                    f"Article demandé : {ligne.article.reference}. "
                    f"Article expédié : "
                    f"{ligne.article_remplacement.reference}. "
                    f"{ligne.commentaire_remplacement or ''}"
                ).strip()

            mouvement = MouvementCreate(
                type="SORTIE",
                article_id=article_sorti_id,
                lot_id=lot_sorti_id,
                affaire_id=preparation.affaire_id,
                emplacement_source_id=emplacement_sortie_id,
                quantite=quantite_sortie,
                motif=f"Expédition {preparation.reference}",
                commentaire=commentaire_sortie,
                operateur=(
                    preparation.preparateur
                    or utilisateur.nom_complet
                ),
                charge_affaires=preparation.affaire.charge_affaires,
                zone_intervention=preparation.affaire.zone_intervention,
                vehicule=preparation.vehicule,
                sortie_libre=False,
            )
            executer_mouvement(
                db,
                mouvement,
                valider_transaction=False,
            )

            ligne.statut = "EXPEDIEE"

        preparation.statut = "EXPEDIEE"
        preparation.date_expedition = datetime.now(timezone.utc)

        notifier_acteurs(
            db,
            preparation,
            "Préparation expédiée",
            (
                f"{preparation.reference} a été expédiée. "
                "Les stocks physiques ont été décrémentés."
            ),
        )

        db.commit()
        return charger_preparation(db, preparation_id)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


ROLES_DECISION_REMPLACEMENT = {
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
    "RESPONSABLE_LOGISTIQUE",
    "RESPONSABLE_PRODUCTION",
    "CHARGE_AFFAIRES",
}


def verifier_decision_remplacement(
    preparation: Preparation,
    utilisateur: Utilisateur,
) -> None:
    est_demandeur = (
        preparation.demandeur is not None
        and preparation.demandeur.strip().casefold()
        == utilisateur.nom_complet.strip().casefold()
    )
    if (
        not est_demandeur
        and utilisateur.role not in ROLES_DECISION_REMPLACEMENT
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Seul le demandeur ou un responsable autorisé peut décider."
            ),
        )


@router.post(
    "/{preparation_id}/lignes/{ligne_id}/remplacement",
    response_model=PreparationRead,
)
def proposer_remplacement(
    preparation_id: int,
    ligne_id: int,
    payload: PropositionRemplacementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    ligne = next(
        (element for element in preparation.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")
    if preparation.statut != "EN_PREPARATION":
        raise HTTPException(
            status_code=409,
            detail="La préparation doit être en cours.",
        )
    if ligne.statut not in {"INDISPONIBLE", "REMPLACEMENT_REFUSE"}:
        raise HTTPException(
            status_code=409,
            detail=(
                "Un remplacement ne peut être proposé que pour une ligne "
                "indisponible ou après un refus."
            ),
        )

    article = db.get(Article, payload.article_remplacement_id)
    if article is None or not article.actif:
        raise HTTPException(
            status_code=404,
            detail="Article de remplacement introuvable.",
        )
    if article.id == ligne.article_id:
        raise HTTPException(
            status_code=422,
            detail="L’article de remplacement doit être différent.",
        )

    emplacement = db.get(
        Emplacement,
        payload.emplacement_remplacement_id,
    )
    if emplacement is None or not emplacement.actif:
        raise HTTPException(
            status_code=404,
            detail="Emplacement de remplacement introuvable.",
        )

    if article_est_beton(db, article):
        if payload.lot_remplacement_id is None:
            raise HTTPException(
                status_code=422,
                detail="Un lot est obligatoire pour un béton de remplacement.",
            )
        lot = db.get(LotBeton, payload.lot_remplacement_id)
        if lot is None or lot.article_id != article.id:
            raise HTTPException(
                status_code=422,
                detail="Le lot ne correspond pas à l’article proposé.",
            )
    elif payload.lot_remplacement_id is not None:
        raise HTTPException(
            status_code=422,
            detail="Aucun lot n’est attendu pour cet article.",
        )

    ligne.article_remplacement_id = article.id
    ligne.lot_remplacement_id = payload.lot_remplacement_id
    ligne.emplacement_remplacement_id = (
        payload.emplacement_remplacement_id
    )
    ligne.quantite_remplacement = payload.quantite_remplacement
    ligne.commentaire_remplacement = (
        payload.commentaire_remplacement.strip()
    )
    ligne.propose_par = utilisateur.nom_complet
    ligne.date_proposition_remplacement = datetime.now(timezone.utc)
    ligne.decision_remplacement = None
    ligne.decision_par = None
    ligne.commentaire_decision = None
    ligne.date_decision_remplacement = None
    ligne.statut = "REMPLACEMENT_PROPOSE"

    creer_notification(
        db,
        preparation.demandeur,
        "Remplacement à valider",
        (
            f"{preparation.reference} — {ligne.article.reference} : "
            f"{article.reference} est proposé en remplacement."
        ),
        f"/preparations?preparation={preparation.id}",
        "ACTION",
    )

    db.commit()
    return charger_preparation(db, preparation_id)


@router.post(
    "/{preparation_id}/lignes/{ligne_id}/remplacement/accepter",
    response_model=PreparationRead,
)
def accepter_remplacement(
    preparation_id: int,
    ligne_id: int,
    payload: DecisionRemplacementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    verifier_decision_remplacement(preparation, utilisateur)

    ligne = next(
        (element for element in preparation.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")
    if ligne.statut != "REMPLACEMENT_PROPOSE":
        raise HTTPException(
            status_code=409,
            detail="Aucun remplacement n’est en attente.",
        )

    try:
        transferer_reservation_remplacement(
            db,
            preparation,
            ligne,
            utilisateur.nom_complet,
        )

        ligne.decision_remplacement = "ACCEPTEE"
        ligne.decision_par = utilisateur.nom_complet
        ligne.commentaire_decision = payload.commentaire_decision
        ligne.date_decision_remplacement = datetime.now(timezone.utc)

        ligne.statut = "A_PREPARER"
        ligne.quantite_preparee = Decimal("0")
        ligne.quantite_manquante = ligne.quantite_demandee
        ligne.motif_ecart = None
        ligne.date_fin_preparation = None

        if preparation.preparateur:
            creer_notification(
                db,
                preparation.preparateur,
                "Remplacement accepté",
                (
                    f"{preparation.reference} — le remplacement proposé pour "
                    f"{ligne.article.reference} a été accepté et réservé."
                ),
                f"/preparations?preparation={preparation.id}",
                "INFORMATION",
            )

        db.commit()
        return charger_preparation(db, preparation_id)
    except HTTPException:
        db.rollback()
        raise


@router.post(
    "/{preparation_id}/lignes/{ligne_id}/remplacement/refuser",
    response_model=PreparationRead,
)
def refuser_remplacement(
    preparation_id: int,
    ligne_id: int,
    payload: DecisionRemplacementCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Preparation:
    preparation = charger_preparation(db, preparation_id)
    verifier_decision_remplacement(preparation, utilisateur)

    ligne = next(
        (element for element in preparation.lignes if element.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable.")
    if ligne.statut != "REMPLACEMENT_PROPOSE":
        raise HTTPException(
            status_code=409,
            detail="Aucun remplacement n’est en attente.",
        )
    if not (payload.commentaire_decision or "").strip():
        raise HTTPException(
            status_code=422,
            detail="Un commentaire est obligatoire pour refuser.",
        )

    ligne.decision_remplacement = "REFUSEE"
    ligne.decision_par = utilisateur.nom_complet
    ligne.commentaire_decision = payload.commentaire_decision.strip()
    ligne.date_decision_remplacement = datetime.now(timezone.utc)
    ligne.statut = "REMPLACEMENT_REFUSE"

    if preparation.preparateur:
        creer_notification(
            db,
            preparation.preparateur,
            "Remplacement refusé",
            (
                f"{preparation.reference} — le remplacement proposé pour "
                f"{ligne.article.reference} a été refusé."
            ),
            f"/preparations?preparation={preparation.id}",
            "ALERTE",
        )

    db.commit()
    return charger_preparation(db, preparation_id)
