from app.schemas.article import ArticleCreate


def test_reference_facultative() -> None:
    article = ArticleCreate(
        designation="Béton dense",
        famille_id=2,
        sous_famille_id=10,
        unite="sac",
        stock_minimum=5,
    )
    assert article.reference is None


def test_reference_manuelle_normalisee() -> None:
    article = ArticleCreate(
        reference=" art-special ",
        designation="Article spécial",
    )
    assert article.reference == "ART-SPECIAL"
