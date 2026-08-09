from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    achats_router, affaires_router, alertes_router, alertes_logistiques_router,
    articles_router, auth_router, dashboard_router, demandes_sortie_router,
    documents_router, documents_fournisseurs_router, documents_materiel_router,
    emplacements_router, familles_router, health_router, inventaires_router,
    inventaires_avances_router, litiges_fournisseurs_router, lots_beton_router,
    magasin_router, maintenance_materiel_router, materiels_router, mouvements_router,
    non_conformites_fournisseurs_router, pilotage_achats_router, preparations_router,
    prets_materiel_router, reapprovisionnement_router, receptions_qualite_router,
    router_notifications, router_reservations, stocks_router, utilisateurs_router,
    valorisation_router,
)
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

for router in (
    health_router, auth_router, achats_router, affaires_router, alertes_router,
    alertes_logistiques_router, articles_router, dashboard_router,
    demandes_sortie_router, documents_router, documents_fournisseurs_router,
    documents_materiel_router, emplacements_router, familles_router,
    inventaires_router, inventaires_avances_router, litiges_fournisseurs_router,
    lots_beton_router, magasin_router, maintenance_materiel_router,
    materiels_router, mouvements_router, non_conformites_fournisseurs_router,
    pilotage_achats_router, preparations_router, prets_materiel_router,
    reapprovisionnement_router, receptions_qualite_router,
    router_notifications, router_reservations, stocks_router,
    utilisateurs_router, valorisation_router,
):
    app.include_router(router)

@app.get('/')
def root() -> dict[str, str]:
    return {'message': settings.app_name, 'version': settings.app_version}
