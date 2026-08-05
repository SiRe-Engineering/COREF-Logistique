from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleRead, ArticleUpdate

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("", response_model=list[ArticleRead])
def lister_articles(
    recherche: str | None = Query(default=None, max_length=100),
    actifs_uniquement: bool = True,
    db: Session = Depends(get_db),
) -> list[Article]:
    requete = select(Article).order_by(Article.reference)

    if actifs_uniquement:
        requete = requete.where(Article.actif.is_(True))

    if recherche:
        terme = f"%{recherche.strip()}%"
        requete = requete.where(
            or_(
                Article.reference.ilike(terme),
                Article.designation.ilike(terme),
            )
        )

    return list(db.scalars(requete).all())


@router.post(
    "",
    response_model=ArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
) -> Article:
    article = Article(**payload.model_dump())
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
def lire_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable.",
        )
    return article


@router.patch("/{article_id}", response_model=ArticleRead)
def modifier_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable.",
        )

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(article, champ, valeur)

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


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def archiver_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> None:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article introuvable.",
        )

    article.actif = False
    db.commit()
