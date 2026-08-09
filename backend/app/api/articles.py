from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.services.valorisation import actualiser_snapshot_mensuel
from app.models.famille import Famille, SousFamille
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate

router = APIRouter(prefix="/api/articles", tags=["Articles"], dependencies=[Depends(utilisateur_courant)])


def verifier_referentiel(
    db: Session,
    famille_id: int | None,
    sous_famille_id: int | None,
) -> None:
    if famille_id is None and sous_famille_id is not None:
        raise HTTPException(
            status_code=422,
            detail="Une sous-famille nécessite une famille.",
        )

    if famille_id is not None:
        famille = db.get(Famille, famille_id)
        if famille is None or not famille.actif:
            raise HTTPException(status_code=404, detail="Famille introuvable.")

    if sous_famille_id is not None:
        sous_famille = db.get(SousFamille, sous_famille_id)
        if sous_famille is None or not sous_famille.actif:
            raise HTTPException(
                status_code=404,
                detail="Sous-famille introuvable.",
            )
        if sous_famille.famille_id != famille_id:
            raise HTTPException(
                status_code=422,
                detail="La sous-famille ne correspond pas à la famille choisie.",
            )


@router.get("", response_model=list[ArticleRead])
def lister_articles(
    recherche: str | None = Query(default=None, max_length=100),
    famille_id: int | None = None,
    sous_famille_id: int | None = None,
    actifs_uniquement: bool = True,
    db: Session = Depends(get_db),
) -> list[Article]:
    requete = (
        select(Article)
        .options(
            joinedload(Article.famille_relation),
            joinedload(Article.sous_famille_relation),
        )
        .order_by(Article.reference)
    )

    if actifs_uniquement:
        requete = requete.where(Article.actif.is_(True))
    if famille_id is not None:
        requete = requete.where(Article.famille_id == famille_id)
    if sous_famille_id is not None:
        requete = requete.where(Article.sous_famille_id == sous_famille_id)
    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                Article.reference.ilike(terme),
                Article.designation.ilike(terme),
            )
        )

    return list(db.scalars(requete).unique().all())


@router.post(
    "",
    response_model=ArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
) -> Article:
    verifier_referentiel(db, payload.famille_id, payload.sous_famille_id)

    donnees = payload.model_dump(exclude_none=True)
    article = Article(**donnees)
    db.add(article)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette référence existe déjà.",
        )

    db.refresh(article)
    return article


@router.get("/{article_id}", response_model=ArticleRead)
def lire_article(article_id: int, db: Session = Depends(get_db)) -> Article:
    requete = (
        select(Article)
        .options(
            joinedload(Article.famille_relation),
            joinedload(Article.sous_famille_relation),
        )
        .where(Article.id == article_id)
    )
    article = db.scalar(requete)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable.")
    return article


@router.patch("/{article_id}", response_model=ArticleRead)
def modifier_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable.")

    donnees = payload.model_dump(exclude_unset=True)
    famille_id = donnees.get("famille_id", article.famille_id)
    sous_famille_id = donnees.get("sous_famille_id", article.sous_famille_id)
    verifier_referentiel(db, famille_id, sous_famille_id)

    for champ, valeur in donnees.items():
        setattr(article, champ, valeur)

    if "cout_unitaire_moyen" in donnees:
        article.date_maj_cout = datetime.now(timezone.utc)
        db.flush()
        actualiser_snapshot_mensuel(db)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette référence existe déjà.",
        )

    db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def archiver_article(article_id: int, db: Session = Depends(get_db)) -> None:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article introuvable.")
    article.actif = False
    db.commit()
