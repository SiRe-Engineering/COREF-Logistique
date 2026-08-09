from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.session import get_db
from app.dependencies import exiger_roles, utilisateur_courant
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.famille import Famille
from app.models.inventaire import Inventaire, LigneInventaire
from app.models.lot_beton import StockLot
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.schemas.inventaire import (
    InventaireCreate,
    InventaireRead,
    LigneInventaireUpdate,
)
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement


router = APIRouter(prefix="/api/inventaires", tags=["Inventaires"])


def generer_nom_inventaire(
    db: Session,
    *,
    type_inventaire: str,
    emplacement: Emplacement | None,
    famille: Famille | None,
) -> str:
    date_du_jour = datetime.now(timezone.utc).date().isoformat()

    if type_inventaire == "EMPLACEMENT":
        if emplacement is None:
            raise HTTPException(
                status_code=422,
                detail="Un emplacement est obligatoire.",
            )
        base_nom = (
            f"{date_du_jour} - Emplacement - {emplacement.nom}"
        )
    elif type_inventaire == "FAMILLE":
        if famille is None:
            raise HTTPException(
                status_code=422,
                detail="Une famille est obligatoire.",
            )
        base_nom = f"{date_du_jour} - Famille - {famille.nom}"
    else:
        base_nom = f"{date_du_jour} - Général"

    noms_existants = set(
        db.scalars(
            select(Inventaire.nom).where(
                Inventaire.nom.like(f"{base_nom}%")
            )
        ).all()
    )

    if base_nom not in noms_existants:
        return base_nom

    suffixe = 2
    while f"{base_nom} ({suffixe})" in noms_existants:
        suffixe += 1

    return f"{base_nom} ({suffixe})"


ROLES_VALIDATION = (
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
    "RESPONSABLE_LOGISTIQUE",
    "RESPONSABLE_PRODUCTION",
)


def charger_inventaire(db: Session, inventaire_id: int) -> Inventaire:
    inventaire = db.scalar(
        select(Inventaire)
        .options(
            joinedload(Inventaire.emplacement),
            joinedload(Inventaire.famille),
            selectinload(Inventaire.lignes).joinedload(
                LigneInventaire.article
            ),
            selectinload(Inventaire.lignes).joinedload(
                LigneInventaire.lot
            ),
            selectinload(Inventaire.lignes).joinedload(
                LigneInventaire.emplacement
            ),
        )
        .where(Inventaire.id == inventaire_id)
    )
    if inventaire is None:
        raise HTTPException(
            status_code=404,
            detail="Inventaire introuvable.",
        )
    return inventaire


def articles_autorises(
    db: Session,
    famille_id: int | None,
) -> set[int] | None:
    if famille_id is None:
        return None
    return set(
        db.scalars(
            select(Article.id).where(
                Article.famille_id == famille_id,
                Article.actif.is_(True),
            )
        ).all()
    )


def ajouter_lignes_emplacement(
    db: Session,
    inventaire: Inventaire,
    emplacement_id: int,
    article_ids: set[int] | None,
) -> None:
    stocks = list(
        db.scalars(
            select(Stock).where(
                Stock.emplacement_id == emplacement_id
            )
        ).all()
    )

    for stock in stocks:
        if article_ids is not None and stock.article_id not in article_ids:
            continue

        article = db.get(Article, stock.article_id)
        if article is None or not article.actif:
            continue

        lots = list(
            db.scalars(
                select(StockLot)
                .where(
                    StockLot.emplacement_id == emplacement_id,
                    StockLot.lot.has(article_id=article.id),
                )
                .order_by(StockLot.lot_id)
            ).all()
        )

        if lots:
            for stock_lot in lots:
                inventaire.lignes.append(
                    LigneInventaire(
                        emplacement_id=emplacement_id,
                        article_id=article.id,
                        lot_id=stock_lot.lot_id,
                        quantite_theorique=(
                            stock_lot.quantite_physique
                            or Decimal("0")
                        ),
                    )
                )
        else:
            inventaire.lignes.append(
                LigneInventaire(
                    emplacement_id=emplacement_id,
                    article_id=article.id,
                    lot_id=None,
                    quantite_theorique=(
                        stock.quantite_physique or Decimal("0")
                    ),
                )
            )


@router.get("", response_model=list[InventaireRead])
def lister_inventaires(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> list[Inventaire]:
    inventaires = db.scalars(
        select(Inventaire)
        .options(
            joinedload(Inventaire.emplacement),
            joinedload(Inventaire.famille),
            selectinload(Inventaire.lignes),
        )
        .order_by(Inventaire.date_creation.desc())
    ).unique().all()
    return list(inventaires)


@router.post(
    "",
    response_model=InventaireRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_inventaire(
    payload: InventaireCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
) -> Inventaire:
    emplacement = None
    famille = None

    if payload.emplacement_id is not None:
        emplacement = db.get(Emplacement, payload.emplacement_id)
        if emplacement is None or not emplacement.actif:
            raise HTTPException(
                status_code=404,
                detail="Emplacement introuvable.",
            )

    if payload.famille_id is not None:
        famille = db.get(Famille, payload.famille_id)
        if famille is None or not famille.actif:
            raise HTTPException(
                status_code=404,
                detail="Famille introuvable.",
            )

    nom_genere = generer_nom_inventaire(
        db,
        type_inventaire=payload.type,
        emplacement=emplacement,
        famille=famille,
    )

    inventaire = Inventaire(
        nom=nom_genere,
        type=payload.type,
        emplacement_id=payload.emplacement_id,
        famille_id=payload.famille_id,
        operateur=payload.operateur or utilisateur.nom_complet,
        commentaire=payload.commentaire,
        statut="EN_COURS",
    )
    db.add(inventaire)
    db.flush()

    article_ids = articles_autorises(db, payload.famille_id)

    if payload.type == "EMPLACEMENT":
        ajouter_lignes_emplacement(
            db,
            inventaire,
            payload.emplacement_id,
            article_ids,
        )
    else:
        emplacement_ids = list(
            db.scalars(
                select(Emplacement.id)
                .where(Emplacement.actif.is_(True))
                .order_by(Emplacement.code)
            ).all()
        )
        for emplacement_id in emplacement_ids:
            ajouter_lignes_emplacement(
                db,
                inventaire,
                emplacement_id,
                article_ids,
            )

    if not inventaire.lignes:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Aucune ligne de stock ne correspond au périmètre choisi.",
        )

    db.commit()
    return charger_inventaire(db, inventaire.id)


@router.patch(
    "/{inventaire_id}/lignes/{ligne_id}",
    response_model=InventaireRead,
)
def saisir_comptage(
    inventaire_id: int,
    ligne_id: int,
    payload: LigneInventaireUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> Inventaire:
    inventaire = charger_inventaire(db, inventaire_id)

    if inventaire.statut != "EN_COURS":
        raise HTTPException(
            status_code=409,
            detail="Cet inventaire ne peut plus être modifié.",
        )

    ligne = next(
        (
            element
            for element in inventaire.lignes
            if element.id == ligne_id
        ),
        None,
    )
    if ligne is None:
        raise HTTPException(
            status_code=404,
            detail="Ligne introuvable.",
        )

    ligne.quantite_comptee = payload.quantite_comptee
    ligne.commentaire = payload.commentaire
    db.commit()
    return charger_inventaire(db, inventaire_id)


@router.post(
    "/{inventaire_id}/valider",
    response_model=InventaireRead,
)
def valider_inventaire(
    inventaire_id: int,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(
        exiger_roles(*ROLES_VALIDATION)
    ),
) -> Inventaire:
    inventaire = charger_inventaire(db, inventaire_id)

    if inventaire.statut != "EN_COURS":
        raise HTTPException(
            status_code=409,
            detail="Cet inventaire est déjà clôturé.",
        )

    non_comptees = [
        ligne
        for ligne in inventaire.lignes
        if ligne.quantite_comptee is None
    ]
    if non_comptees:
        raise HTTPException(
            status_code=422,
            detail=(
                f"{len(non_comptees)} ligne(s) doivent encore être comptées."
            ),
        )

    try:
        for ligne in inventaire.lignes:
            ecart = ligne.ecart or Decimal("0")
            if ecart == 0:
                continue

            mouvement = MouvementCreate(
                type=(
                    "AJUSTEMENT_POSITIF"
                    if ecart > 0
                    else "AJUSTEMENT_NEGATIF"
                ),
                article_id=ligne.article_id,
                lot_id=ligne.lot_id,
                inventaire_id=inventaire.id,
                emplacement_source_id=(
                    ligne.emplacement_id if ecart < 0 else None
                ),
                emplacement_destination_id=(
                    ligne.emplacement_id if ecart > 0 else None
                ),
                quantite=abs(ecart),
                motif=f"Validation {inventaire.reference}",
                commentaire=ligne.commentaire,
                operateur=utilisateur.nom_complet,
            )
            executer_mouvement(
                db,
                mouvement,
                valider_transaction=False,
            )

        inventaire.statut = "VALIDE"
        inventaire.valide_par = utilisateur.nom_complet
        inventaire.date_validation = datetime.now(timezone.utc)

        db.commit()
        return charger_inventaire(db, inventaire_id)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
