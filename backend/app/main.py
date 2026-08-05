from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    affaires_router,
    articles_router,
    emplacements_router,
    familles_router,
    health_router,
    lots_beton_router,
    mouvements_router,
    stocks_router,
)
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(familles_router)
app.include_router(emplacements_router)
app.include_router(stocks_router)
app.include_router(lots_beton_router)
app.include_router(affaires_router)
app.include_router(mouvements_router)
app.include_router(articles_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "version": settings.app_version,
    }
