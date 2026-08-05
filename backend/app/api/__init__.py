from app.api.articles import router as articles_router
from app.api.emplacements import router as emplacements_router
from app.api.familles import router as familles_router
from app.api.health import router as health_router

__all__ = [
    "articles_router",
    "emplacements_router",
    "familles_router",
    "health_router",
]
