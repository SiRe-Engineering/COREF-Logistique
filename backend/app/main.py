from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    affaires_router,
    articles_router,
    auth_router,
    emplacements_router,
    demandes_sortie_router,
    dashboard_router,
    familles_router,
    health_router,
    inventaires_router,
    lots_beton_router,
    magasin_router,
    materiels_router,
    mouvements_router,
    preparations_router,
    router_notifications,
    router_reservations,
    stocks_router,
    utilisateurs_router,
    valorisation_router,
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
app.include_router(auth_router)
app.include_router(utilisateurs_router)
app.include_router(familles_router)
app.include_router(emplacements_router)
app.include_router(demandes_sortie_router)
app.include_router(dashboard_router)
app.include_router(stocks_router)
app.include_router(router_reservations)
app.include_router(router_notifications)
app.include_router(lots_beton_router)
app.include_router(magasin_router)
app.include_router(affaires_router)
app.include_router(materiels_router)
app.include_router(inventaires_router)
app.include_router(preparations_router)
app.include_router(mouvements_router)
app.include_router(articles_router)
app.include_router(valorisation_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "version": settings.app_version,
    }
