from app.api.articles import router as articles_router
from app.api.stocks import router as stocks_router
from app.api.emplacements import router as emplacements_router
from app.api.familles import router as familles_router
from app.api.affaires import router as affaires_router
from app.api.lots_beton import router as lots_beton_router
from app.api.materiels import router as materiels_router
from app.api.mouvements import router as mouvements_router


def test_core_routers_have_auth_dependency() -> None:
    routers = [
        articles_router,
        stocks_router,
        emplacements_router,
        familles_router,
        affaires_router,
        lots_beton_router,
        materiels_router,
        mouvements_router,
    ]

    for router in routers:
        assert router.dependencies, f"{router.prefix} doit imposer une authentification"
