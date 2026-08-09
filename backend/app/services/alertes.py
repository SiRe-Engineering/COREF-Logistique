from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.alerte import AlerteLogistique
from app.models.article import Article
from app.models.inventaire import Inventaire
from app.models.lot_beton import LotBeton
from app.models.preparation import Preparation
from app.models.stock import Stock


STATUTS_PREPARATION_OUVERTS = {
    "BROUILLON",
    "A_PREPARER",
    "EN_PREPARATION",
    "PRETE",
    "VALIDEE",
}
STATUTS_LIGNE_BLOQUEE = {
    "PARTIELLE",
    "INDISPONIBLE",
    "REMPLACEMENT_PROPOSE",
}
HORIZON_PEREMPTION_JOURS = 60
ANCIENNETE_INVENTAIRE_JOURS = 7


@dataclass(frozen=True)
class SignalAlerte:
    cle: str
    categorie: str
    niveau: str
    titre: str
    message: str
    lien: str | None
    source_type: str | None
    source_id: int | None


def _signaux_stock(db: Session) -> list[SignalAlerte]:
    lignes = db.execute(
        select(
            Article.id,
            Article.reference,
            Article.designation,
            Article.unite,
            Article.stock_minimum,
            Article.seuil_alerte,
            func.coalesce(func.sum(Stock.quantite_physique), 0),
            func.coalesce(func.sum(Stock.quantite_reservee), 0),
        )
        .outerjoin(Stock, Stock.article_id == Article.id)
        .where(Article.actif.is_(True))
        .group_by(Article.id)
    ).all()

    resultats: list[SignalAlerte] = []
    for (
        article_id,
        reference,
        designation,
        unite,
        stock_minimum,
        seuil_alerte,
        physique,
        reservee,
    ) in lignes:
        disponible = Decimal(physique or 0) - Decimal(reservee or 0)
        seuil = max(
            Decimal(stock_minimum or 0),
            Decimal(seuil_alerte or 0),
        )

        if disponible <= 0:
            resultats.append(
                SignalAlerte(
                    cle=f"STOCK:RUPTURE:{article_id}",
                    categorie="STOCK",
                    niveau="CRITIQUE",
                    titre=f"Rupture — {reference}",
                    message=(
                        f"{designation} : {disponible} {unite} disponible."
                    ),
                    lien="/stocks",
                    source_type="ARTICLE",
                    source_id=article_id,
                )
            )
        elif seuil > 0 and disponible <= seuil:
            resultats.append(
                SignalAlerte(
                    cle=f"STOCK:SEUIL:{article_id}",
                    categorie="STOCK",
                    niveau="AVERTISSEMENT",
                    titre=f"Stock sous seuil — {reference}",
                    message=(
                        f"{designation} : {disponible} {unite} disponible "
                        f"pour un seuil de {seuil} {unite}."
                    ),
                    lien="/stocks",
                    source_type="ARTICLE",
                    source_id=article_id,
                )
            )

    return resultats


def _signaux_lots(db: Session, aujourd_hui: date) -> list[SignalAlerte]:
    horizon = aujourd_hui + timedelta(days=HORIZON_PEREMPTION_JOURS)
    lots = list(
        db.scalars(
            select(LotBeton)
            .options(selectinload(LotBeton.stocks))
            .where(
                LotBeton.actif.is_(True),
                LotBeton.supprime.is_(False),
                LotBeton.date_peremption <= horizon,
            )
        ).unique().all()
    )

    resultats: list[SignalAlerte] = []
    for lot in lots:
        physique = sum(
            (
                stock.quantite_physique or Decimal("0")
                for stock in lot.stocks
            ),
            Decimal("0"),
        )
        if physique <= 0:
            continue

        jours = (lot.date_peremption - aujourd_hui).days
        if jours < 0:
            niveau = "CRITIQUE"
            titre = f"Lot périmé — {lot.reference_interne}"
            detail = f"périmé depuis {abs(jours)} jour(s)"
        elif jours <= 30:
            niveau = "CRITIQUE"
            titre = f"Péremption proche — {lot.reference_interne}"
            detail = f"péremption dans {jours} jour(s)"
        else:
            niveau = "AVERTISSEMENT"
            titre = f"Lot à surveiller — {lot.reference_interne}"
            detail = f"péremption dans {jours} jour(s)"

        resultats.append(
            SignalAlerte(
                cle=f"LOT:PEREMPTION:{lot.id}",
                categorie="PEREMPTION",
                niveau=niveau,
                titre=titre,
                message=(
                    f"{lot.article.reference} — {lot.article.designation}, "
                    f"lot fournisseur {lot.numero_lot_fournisseur} : "
                    f"{detail}, {physique} {lot.article.unite} en stock."
                ),
                lien="/lots-beton",
                source_type="LOT",
                source_id=lot.id,
            )
        )

    return resultats


def _signaux_preparations(
    db: Session,
    aujourd_hui: date,
) -> list[SignalAlerte]:
    preparations = list(
        db.scalars(
            select(Preparation)
            .options(selectinload(Preparation.lignes))
            .where(
                Preparation.statut.in_(STATUTS_PREPARATION_OUVERTS)
            )
        ).unique().all()
    )

    resultats: list[SignalAlerte] = []
    for preparation in preparations:
        if (
            preparation.date_besoin is not None
            and preparation.date_besoin < aujourd_hui
        ):
            retard = (aujourd_hui - preparation.date_besoin).days
            resultats.append(
                SignalAlerte(
                    cle=f"PREPARATION:RETARD:{preparation.id}",
                    categorie="PREPARATION",
                    niveau="CRITIQUE",
                    titre=f"Préparation en retard — {preparation.reference}",
                    message=(
                        f"{preparation.nom} : date de besoin dépassée de "
                        f"{retard} jour(s)."
                    ),
                    lien="/preparations",
                    source_type="PREPARATION",
                    source_id=preparation.id,
                )
            )

        bloquees = [
            ligne
            for ligne in preparation.lignes
            if ligne.statut in STATUTS_LIGNE_BLOQUEE
        ]
        if bloquees:
            resultats.append(
                SignalAlerte(
                    cle=f"PREPARATION:BLOQUEE:{preparation.id}",
                    categorie="PREPARATION",
                    niveau="AVERTISSEMENT",
                    titre=f"Préparation bloquée — {preparation.reference}",
                    message=(
                        f"{len(bloquees)} ligne(s) nécessitent une action "
                        f"avant finalisation."
                    ),
                    lien="/preparations",
                    source_type="PREPARATION",
                    source_id=preparation.id,
                )
            )

    return resultats


def _signaux_inventaires(
    db: Session,
    maintenant: datetime,
) -> list[SignalAlerte]:
    limite = maintenant - timedelta(days=ANCIENNETE_INVENTAIRE_JOURS)
    inventaires = list(
        db.scalars(
            select(Inventaire).where(
                Inventaire.statut == "EN_COURS",
                Inventaire.date_creation < limite,
            )
        ).all()
    )

    resultats: list[SignalAlerte] = []
    for inventaire in inventaires:
        anciennete = max(
            0,
            (maintenant.date() - inventaire.date_creation.date()).days,
        )
        resultats.append(
            SignalAlerte(
                cle=f"INVENTAIRE:ANCIEN:{inventaire.id}",
                categorie="INVENTAIRE",
                niveau="AVERTISSEMENT",
                titre=f"Inventaire à clôturer — {inventaire.reference}",
                message=(
                    f"{inventaire.nom} est en cours depuis "
                    f"{anciennete} jour(s)."
                ),
                lien="/inventaires",
                source_type="INVENTAIRE",
                source_id=inventaire.id,
            )
        )

    return resultats


def detecter_signaux(db: Session) -> list[SignalAlerte]:
    maintenant = datetime.now(timezone.utc)
    aujourd_hui = maintenant.date()
    return [
        *_signaux_stock(db),
        *_signaux_lots(db, aujourd_hui),
        *_signaux_preparations(db, aujourd_hui),
        *_signaux_inventaires(db, maintenant),
    ]


def synchroniser_alertes(db: Session) -> None:
    maintenant = datetime.now(timezone.utc)
    signaux = detecter_signaux(db)
    actifs = {signal.cle: signal for signal in signaux}

    existantes = {
        alerte.cle: alerte
        for alerte in db.scalars(
            select(AlerteLogistique)
        ).all()
    }

    for cle, signal in actifs.items():
        alerte = existantes.get(cle)
        if alerte is None:
            db.add(
                AlerteLogistique(
                    cle=signal.cle,
                    categorie=signal.categorie,
                    niveau=signal.niveau,
                    titre=signal.titre,
                    message=signal.message,
                    lien=signal.lien,
                    source_type=signal.source_type,
                    source_id=signal.source_id,
                    statut="ACTIVE",
                    date_derniere_detection=maintenant,
                )
            )
            continue

        # A previously resolved alert becomes active again if the
        # underlying condition reappears.
        if alerte.statut == "RESOLUE":
            alerte.statut = "ACTIVE"
            alerte.acquittee_par = None
            alerte.date_acquittement = None
            alerte.date_resolution = None
            alerte.date_premiere_detection = maintenant

        alerte.categorie = signal.categorie
        alerte.niveau = signal.niveau
        alerte.titre = signal.titre
        alerte.message = signal.message
        alerte.lien = signal.lien
        alerte.source_type = signal.source_type
        alerte.source_id = signal.source_id
        alerte.date_derniere_detection = maintenant

    for cle, alerte in existantes.items():
        if cle not in actifs and alerte.statut != "RESOLUE":
            alerte.statut = "RESOLUE"
            alerte.date_resolution = maintenant

    db.flush()
