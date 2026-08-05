from app.api.affaires import router as affaires_router
from app.api.articles import router as articles_router
from app.api.auth import router as auth_router
from app.api.emplacements import router as emplacements_router
from app.api.demandes_sortie import router as demandes_sortie_router
from app.api.familles import router as familles_router
from app.api.health import router as health_router
from app.api.inventaires import router as inventaires_router
from app.api.lots_beton import router as lots_beton_router
from app.api.materiels import router as materiels_router
from app.api.mouvements import router as mouvements_router
from app.api.preparations import router as preparations_router
from app.api.reservations import (
    router_notifications,
    router_reservations,
)
from app.api.stocks import router as stocks_router
from app.api.utilisateurs import router as utilisateurs_router

__all__ = [
    "affaires_router",
    "articles_router",
    "auth_router",
    "emplacements_router",
    "demandes_sortie_router",
    "familles_router",
    "health_router",
    "inventaires_router",
    "lots_beton_router",
    "materiels_router",
    "mouvements_router",
    "preparations_router",
    "router_notifications",
    "router_reservations",
    "stocks_router",
    "utilisateurs_router",
]
