from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.lot_beton import LotBeton, StockLot
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.schemas.magasin import (
    ScanArticleRead,
    ScanEmplacementRead,
    ScanLotRead,
    ScanResultatRead,
)


router = APIRouter(prefix="/api/magasin", tags=["Mode magasin"])


def normaliser_scan(valeur: str) -> str:
    return valeur.strip()


def emplacements_article(
    db: Session,
    article_id: int,
) -> list[ScanEmplacementRead]:
    stocks = db.execute(
        select(Stock, Emplacement)
        .join(Emplacement, Emplacement.id == Stock.emplacement_id)
        .where(
            Stock.article_id == article_id,
            Emplacement.actif.is_(True),
        )
        .order_by(Emplacement.code)
    ).all()

    return [
        ScanEmplacementRead(
            id=emplacement.id,
            code=emplacement.code,
            nom=emplacement.nom,
            quantite_physique=stock.quantite_physique or Decimal("0"),
            quantite_reservee=stock.quantite_reservee or Decimal("0"),
            quantite_disponible=stock.quantite_disponible,
        )
        for stock, emplacement in stocks
    ]


def resultat_article(
    db: Session,
    article: Article,
    valeur: str,
) -> ScanResultatRead:
    emplacements = emplacements_article(db, article.id)
    physique = sum(
        (item.quantite_physique for item in emplacements),
        Decimal("0"),
    )
    reservee = sum(
        (item.quantite_reservee for item in emplacements),
        Decimal("0"),
    )

    return ScanResultatRead(
        type="ARTICLE",
        valeur=valeur,
        article=ScanArticleRead(
            id=article.id,
            reference=article.reference,
            designation=article.designation,
            unite=article.unite,
            famille=article.famille,
            sous_famille=article.sous_famille,
            quantite_physique=physique,
            quantite_reservee=reservee,
            quantite_disponible=physique - reservee,
            emplacements=emplacements,
        ),
    )


def resultat_lot(
    db: Session,
    lot: LotBeton,
    valeur: str,
) -> ScanResultatRead:
    stocks = db.execute(
        select(StockLot, Emplacement)
        .join(Emplacement, Emplacement.id == StockLot.emplacement_id)
        .where(
            StockLot.lot_id == lot.id,
            Emplacement.actif.is_(True),
        )
        .order_by(Emplacement.code)
    ).all()

    emplacements = [
        ScanEmplacementRead(
            id=emplacement.id,
            code=emplacement.code,
            nom=emplacement.nom,
            quantite_physique=stock.quantite_physique or Decimal("0"),
            quantite_reservee=stock.quantite_reservee or Decimal("0"),
            quantite_disponible=stock.quantite_disponible,
        )
        for stock, emplacement in stocks
    ]

    return ScanResultatRead(
        type="LOT",
        valeur=valeur,
        lot=ScanLotRead(
            id=lot.id,
            reference_interne=lot.reference_interne,
            numero_lot_fournisseur=lot.numero_lot_fournisseur,
            article_id=lot.article.id,
            article_reference=lot.article.reference,
            article_designation=lot.article.designation,
            unite=lot.article.unite,
            date_peremption=lot.date_peremption.isoformat(),
            emplacements=emplacements,
        ),
    )


@router.get("/scan/{valeur:path}", response_model=ScanResultatRead)
def scanner(
    valeur: str,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
) -> ScanResultatRead:
    code = normaliser_scan(valeur)
    if not code:
        raise HTTPException(status_code=422, detail="Code vide.")

    article = db.scalar(
        select(Article).where(
            Article.actif.is_(True),
            func.lower(Article.reference) == code.lower(),
        )
    )
    if article is not None:
        return resultat_article(db, article, code)

    lot = db.scalar(
        select(LotBeton).where(
            LotBeton.actif.is_(True),
            LotBeton.supprime.is_(False),
            or_(
                func.lower(LotBeton.reference_interne) == code.lower(),
                func.lower(LotBeton.numero_lot_fournisseur)
                == code.lower(),
            ),
        )
    )
    if lot is not None:
        return resultat_lot(db, lot, code)

    # Manual search fallback: unique article match.
    articles = list(
        db.scalars(
            select(Article)
            .where(
                Article.actif.is_(True),
                or_(
                    Article.reference.ilike(f"%{code}%"),
                    Article.designation.ilike(f"%{code}%"),
                ),
            )
            .limit(2)
        ).all()
    )
    if len(articles) == 1:
        return resultat_article(db, articles[0], code)

    raise HTTPException(
        status_code=404,
        detail=(
            "Aucun article ou lot unique ne correspond à ce code. "
            "Scannez la référence exacte."
        ),
    )
