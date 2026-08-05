from app.api.affaires import router as affaires_router
from app.api.articles import router as articles_router
from app.api.emplacements import router as emplacements_router
from app.api.familles import router as familles_router
from app.api.health import router as health_router
from app.api.lots_beton import router as lots_beton_router
from app.api.mouvements import router as mouvements_router
from app.api.stocks import router as stocks_router

__all__ = [
    "affaires_router",
    "articles_router",
    "emplacements_router",
    "familles_router",
    "health_router",
    "lots_beton_router",
    "mouvements_router",
    "stocks_router",
]
