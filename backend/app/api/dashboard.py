from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.models.inventaire import Inventaire
from app.models.lot_beton import LotBeton, StockLot
from app.models.preparation import Preparation
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.schemas.dashboard import (
    DashboardInventaireRead,
    DashboardKpiRead,
    DashboardLotAlerteRead,
    DashboardPreparationRead,
    DashboardRead,
    DashboardStockAlerteRead,
)


router = APIRouter(prefix="/api/dashboard", tags=["Tableau de bord"])

STATUTS_PREPARATION_ACTIFS = {
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


@router.get("", response_model=DashboardRead)
def tableau_de_bord(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> DashboardRead:
    aujourd_hui = date.today()

    articles = list(
        db.scalars(
            select(Article)
            .where(Article.actif.is_(True))
            .order_by(Article.designation)
        ).all()
    )

    totaux_stock = {
        article_id: (physique or Decimal("0"), reservee or Decimal("0"))
        for article_id, physique, reservee in db.execute(
            select(
                Stock.article_id,
                func.sum(Stock.quantite_physique),
                func.sum(Stock.quantite_reservee),
            ).group_by(Stock.article_id)
        ).all()
    }

    alertes_stock: list[DashboardStockAlerteRead] = []
    ruptures = 0
    sous_seuil = 0

    for article in articles:
        physique, reservee = totaux_stock.get(
            article.id,
            (Decimal("0"), Decimal("0")),
        )
        disponible = physique - reservee
        seuil = article.seuil_alerte or article.stock_minimum or Decimal("0")

        if disponible <= 0:
            ruptures += 1
            alertes_stock.append(
                DashboardStockAlerteRead(
                    article_id=article.id,
                    reference=article.reference,
                    designation=article.designation,
                    unite=article.unite,
                    disponible=disponible,
                    seuil=seuil,
                    niveau="RUPTURE",
                )
            )
        elif seuil > 0 and disponible <= seuil:
            sous_seuil += 1
            alertes_stock.append(
                DashboardStockAlerteRead(
                    article_id=article.id,
                    reference=article.reference,
                    designation=article.designation,
                    unite=article.unite,
                    disponible=disponible,
                    seuil=seuil,
                    niveau="SOUS_SEUIL",
                )
            )

    alertes_stock.sort(
        key=lambda item: (
            0 if item.niveau == "RUPTURE" else 1,
            item.designation.lower(),
        )
    )

    valeur_stock_physique = Decimal("0")
    valeur_stock_reservee = Decimal("0")
    for article in articles:
        physique, reservee = totaux_stock.get(
            article.id,
            (Decimal("0"), Decimal("0")),
        )
        cout = article.cout_unitaire_moyen or Decimal("0")
        valeur_stock_physique += physique * cout
        valeur_stock_reservee += reservee * cout

    valeur_stock_disponible = (
        valeur_stock_physique - valeur_stock_reservee
    )

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
            .order_by(LotBeton.date_peremption)
        ).unique().all()
    )

    alertes_lots: list[DashboardLotAlerteRead] = []
    for lot in lots:
        quantite = sum(
            (stock.quantite_physique or Decimal("0") for stock in lot.stocks),
            Decimal("0"),
        )
        if quantite <= 0:
            continue
        jours = (lot.date_peremption - aujourd_hui).days
        alertes_lots.append(
            DashboardLotAlerteRead(
                lot_id=lot.id,
                reference_interne=lot.reference_interne,
                numero_lot_fournisseur=lot.numero_lot_fournisseur,
                article_reference=lot.article.reference,
                article_designation=lot.article.designation,
                date_peremption=lot.date_peremption,
                jours_restants=jours,
                quantite_physique=quantite,
                niveau=(
                    "PERIME"
                    if jours < 0
                    else "CRITIQUE"
                    if jours <= 30
                    else "A_SURVEILLER"
                ),
            )
        )

    preparations = list(
        db.scalars(
            select(Preparation)
            .options(selectinload(Preparation.lignes))
            .where(Preparation.statut.in_(STATUTS_PREPARATION_ACTIFS))
            .order_by(Preparation.date_besoin, Preparation.date_creation)
        ).unique().all()
    )

    preparations_dashboard: list[DashboardPreparationRead] = []
    preparations_retard = 0
    retours_en_attente = 0

    for preparation in preparations:
        retard = bool(
            preparation.date_besoin
            and preparation.date_besoin < aujourd_hui
        )
        if retard:
            preparations_retard += 1

        bloquees = sum(
            1
            for ligne in preparation.lignes
            if ligne.statut in STATUTS_LIGNE_BLOQUEE
        )

        retours_en_attente += sum(
            1
            for ligne in preparation.lignes
            if (ligne.quantite_expediee or Decimal("0"))
            > (ligne.quantite_retournee or Decimal("0"))
        )

        preparations_dashboard.append(
            DashboardPreparationRead(
                id=preparation.id,
                reference=preparation.reference,
                nom=preparation.nom,
                statut=preparation.statut,
                date_besoin=preparation.date_besoin,
                demandeur=preparation.demandeur,
                preparateur=preparation.preparateur,
                en_retard=retard,
                lignes_bloquees=bloquees,
            )
        )

    inventaires = list(
        db.scalars(
            select(Inventaire)
            .options(selectinload(Inventaire.lignes))
            .where(Inventaire.statut == "EN_COURS")
            .order_by(Inventaire.date_creation)
        ).unique().all()
    )

    inventaires_dashboard = [
        DashboardInventaireRead(
            id=inventaire.id,
            reference=inventaire.reference,
            nom=inventaire.nom,
            operateur=inventaire.operateur,
            lignes_total=len(inventaire.lignes),
            lignes_comptees=sum(
                1
                for ligne in inventaire.lignes
                if ligne.quantite_comptee is not None
            ),
        )
        for inventaire in inventaires
    ]

    valeur_lots_a_perimer = sum(
        (
            item.quantite_physique
            * (
                db.get(Article, next(
                    lot.article_id
                    for lot in lots
                    if lot.id == item.lot_id
                )).cout_unitaire_moyen
                or Decimal("0")
            )
            for item in alertes_lots
        ),
        Decimal("0"),
    )

    return DashboardRead(
        date_reference=aujourd_hui,
        kpis=DashboardKpiRead(
            articles_actifs=len(articles),
            ruptures=ruptures,
            stocks_sous_seuil=sous_seuil,
            lots_a_perimer=len(alertes_lots),
            preparations_a_traiter=len(preparations),
            preparations_en_retard=preparations_retard,
            inventaires_en_cours=len(inventaires),
            retours_en_attente=retours_en_attente,
            valeur_stock_physique=valeur_stock_physique,
            valeur_stock_reservee=valeur_stock_reservee,
            valeur_stock_disponible=valeur_stock_disponible,
            valeur_lots_a_perimer=valeur_lots_a_perimer,
        ),
        stocks=alertes_stock[:30],
        lots=alertes_lots[:30],
        preparations=preparations_dashboard[:30],
        inventaires=inventaires_dashboard[:20],
    )
