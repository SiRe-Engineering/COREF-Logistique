from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.stock import Stock
from app.models.valorisation import SnapshotValorisationStock


def mois_courant() -> date:
    aujourd_hui = date.today()
    return aujourd_hui.replace(day=1)


def calculer_valorisation_globale(
    db: Session,
) -> tuple[Decimal, Decimal, Decimal]:
    ligne = db.execute(
        select(
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
        .where(Article.actif.is_(True))
    ).one()

    physique = Decimal(ligne[0] or 0).quantize(Decimal("0.01"))
    reservee = Decimal(ligne[1] or 0).quantize(Decimal("0.01"))
    disponible = (physique - reservee).quantize(Decimal("0.01"))

    return physique, reservee, disponible


def actualiser_snapshot_mensuel(
    db: Session,
) -> SnapshotValorisationStock:
    mois = mois_courant()
    physique, reservee, disponible = calculer_valorisation_globale(db)

    snapshot = db.scalar(
        select(SnapshotValorisationStock)
        .where(SnapshotValorisationStock.mois == mois)
        .with_for_update(of=SnapshotValorisationStock)
    )

    if snapshot is None:
        snapshot = SnapshotValorisationStock(
            mois=mois,
            valeur_physique=physique,
            valeur_reservee=reservee,
            valeur_disponible=disponible,
            date_mise_a_jour=datetime.now(timezone.utc),
        )
        db.add(snapshot)
    else:
        snapshot.valeur_physique = physique
        snapshot.valeur_reservee = reservee
        snapshot.valeur_disponible = disponible
        snapshot.date_mise_a_jour = datetime.now(timezone.utc)

    db.flush()
    return snapshot
