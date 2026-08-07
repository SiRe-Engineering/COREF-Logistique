from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.models.famille import Famille
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.models.valorisation import SnapshotValorisationStock
from app.schemas.valorisation import (
    ValorisationFamilleRead,
    ValorisationHistoriqueRead,
    ValorisationRead,
    ValorisationResumeRead,
)
from app.services.valorisation import actualiser_snapshot_mensuel


router = APIRouter(
    prefix="/api/valorisation",
    tags=["Valorisation"],
)


def variation_pct(
    actuel: Decimal,
    precedent: Decimal | None,
) -> Decimal | None:
    if precedent is None or precedent == 0:
        return None
    return (
        (actuel - precedent)
        / precedent
        * Decimal("100")
    ).quantize(Decimal("0.1"))


@router.get("", response_model=ValorisationRead)
def lire_valorisation(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> ValorisationRead:
    courant = actualiser_snapshot_mensuel(db)
    db.commit()
    db.refresh(courant)

    historique_db = list(
        db.scalars(
            select(SnapshotValorisationStock)
            .order_by(SnapshotValorisationStock.mois.desc())
            .limit(24)
        ).all()
    )
    historique_db.reverse()

    precedent = (
        historique_db[-2].valeur_physique
        if len(historique_db) >= 2
        else None
    )

    lignes_familles = db.execute(
        select(
            Article.famille_id,
            Famille.nom,
            func.coalesce(
                func.sum(
                    Stock.quantite_physique
                    * Article.cout_unitaire_moyen
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    Stock.quantite_reservee
                    * Article.cout_unitaire_moyen
                ),
                0,
            ),
        )
        .join(Article, Article.id == Stock.article_id)
        .outerjoin(Famille, Famille.id == Article.famille_id)
        .where(Article.actif.is_(True))
        .group_by(Article.famille_id, Famille.nom)
    ).all()

    total_physique = courant.valeur_physique or Decimal("0")
    familles: list[ValorisationFamilleRead] = []

    for famille_id, nom, physique, reservee in lignes_familles:
        physique_decimal = Decimal(physique or 0).quantize(
            Decimal("0.01")
        )
        reservee_decimal = Decimal(reservee or 0).quantize(
            Decimal("0.01")
        )

        familles.append(
            ValorisationFamilleRead(
                famille_id=famille_id,
                famille=nom or "Sans famille",
                valeur_physique=physique_decimal,
                valeur_reservee=reservee_decimal,
                valeur_disponible=(
                    physique_decimal - reservee_decimal
                ).quantize(Decimal("0.01")),
                part_physique_pct=(
                    (
                        physique_decimal
                        / total_physique
                        * Decimal("100")
                    ).quantize(Decimal("0.1"))
                    if total_physique > 0
                    else Decimal("0")
                ),
            )
        )

    familles.sort(
        key=lambda item: item.valeur_physique,
        reverse=True,
    )

    return ValorisationRead(
        resume=ValorisationResumeRead(
            valeur_physique=courant.valeur_physique,
            valeur_reservee=courant.valeur_reservee,
            valeur_disponible=courant.valeur_disponible,
            variation_mensuelle_pct=variation_pct(
                courant.valeur_physique,
                precedent,
            ),
        ),
        historique=[
            ValorisationHistoriqueRead(
                mois=item.mois,
                valeur_physique=item.valeur_physique,
                valeur_reservee=item.valeur_reservee,
                valeur_disponible=item.valeur_disponible,
                date_mise_a_jour=item.date_mise_a_jour,
            )
            for item in historique_db
        ],
        familles=familles,
    )
