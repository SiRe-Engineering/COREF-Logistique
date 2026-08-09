from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.achats import ArticleFournisseur
from app.models.reapprovisionnement import BesoinReapprovisionnement
from app.models.stock import Stock
from app.schemas.reapprovisionnement import SuggestionReapproRead


STATUTS_OUVERTS = {"A_TRAITER", "VALIDE", "COMMANDE"}


def quantite_suggeree(
    *,
    disponible: Decimal,
    minimum: Decimal,
    maximum: Decimal,
    seuil_alerte: Decimal = Decimal("0"),
) -> Decimal:
    """Calcule la quantité proposée.

    Avec un stock maximum, il constitue la cible de remontée.
    Sans stock maximum, un article au seuil reste visible : on propose
    une quantité de sécurité égale à la cible (mini / seuil), tout en
    signalant dans l'interface que le stock maximum doit être défini.
    """
    seuil = max(minimum, seuil_alerte)
    if maximum > 0:
        return max(Decimal("0"), maximum - disponible)

    cible = seuil
    manque = max(Decimal("0"), cible - disponible)
    if disponible <= seuil and cible > 0 and manque == 0:
        return cible
    return manque


def suggestions_reapprovisionnement(
    db: Session,
) -> list[SuggestionReapproRead]:
    # Agréger les stocks dans une sous-requête évite un GROUP BY sur
    # l'entité Article. Article charge ses relations famille/sous-famille
    # en eager loading ; PostgreSQL exigeait alors que toutes les colonnes
    # jointes figurent également dans le GROUP BY.
    stock_agrege = (
        select(
            Stock.article_id.label("article_id"),
            func.coalesce(func.sum(Stock.quantite_physique), 0).label(
                "quantite_physique"
            ),
            func.coalesce(func.sum(Stock.quantite_reservee), 0).label(
                "quantite_reservee"
            ),
        )
        .group_by(Stock.article_id)
        .subquery()
    )

    lignes = db.execute(
        select(
            Article,
            func.coalesce(stock_agrege.c.quantite_physique, 0),
            func.coalesce(stock_agrege.c.quantite_reservee, 0),
        )
        .outerjoin(
            stock_agrege,
            stock_agrege.c.article_id == Article.id,
        )
        .where(Article.actif.is_(True))
        .order_by(Article.reference)
    ).unique().all()

    besoins_ouverts = {
        besoin.article_id: besoin.id
        for besoin in db.scalars(
            select(BesoinReapprovisionnement).where(
                BesoinReapprovisionnement.statut.in_(STATUTS_OUVERTS)
            )
        ).all()
    }


    fournisseurs_preferes = {
        lien.article_id: lien
        for lien in db.scalars(
            select(ArticleFournisseur).where(
                ArticleFournisseur.fournisseur_prefere.is_(True)
            )
        ).unique().all()
    }

    resultats: list[SuggestionReapproRead] = []
    for article, physique_raw, reservee_raw in lignes:
        physique = Decimal(physique_raw or 0)
        reservee = Decimal(reservee_raw or 0)
        disponible = physique - reservee
        minimum = Decimal(article.stock_minimum or 0)
        maximum = Decimal(article.stock_maximum or 0)
        seuil = max(minimum, Decimal(article.seuil_alerte or 0))

        if disponible <= 0:
            niveau = "RUPTURE"
        elif seuil > 0 and disponible <= seuil:
            niveau = "SOUS_SEUIL"
        else:
            continue

        suggeree = quantite_suggeree(
            disponible=disponible,
            minimum=minimum,
            maximum=maximum,
            seuil_alerte=Decimal(article.seuil_alerte or 0),
        )
        if suggeree <= 0:
            continue

        prefere = fournisseurs_preferes.get(article.id)

        resultats.append(
            SuggestionReapproRead(
                article=article,
                quantite_physique=physique,
                quantite_reservee=reservee,
                quantite_disponible=disponible,
                quantite_suggeree=suggeree,
                niveau=niveau,
                besoin_ouvert_id=besoins_ouverts.get(article.id),
                fournisseur_prefere_id=(
                    prefere.fournisseur_id if prefere else None
                ),
                fournisseur_prefere=(
                    prefere.fournisseur.raison_sociale
                    if prefere
                    else None
                ),
                fournisseur_prefere_code=(
                    prefere.fournisseur.code if prefere else None
                ),
                reference_fournisseur=(
                    prefere.reference_fournisseur if prefere else None
                ),
                prix_suggere=(
                    prefere.prix_unitaire_ht if prefere else None
                ),
                delai_jours=(prefere.delai_jours if prefere else None),
            )
        )

    return resultats
