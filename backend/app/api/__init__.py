from app.api.achats import router as achats_router
from app.api.affaires import router as affaires_router
from app.api.alertes import router as alertes_router
from app.api.alertes_logistiques import router as alertes_logistiques_router
from app.api.articles import router as articles_router
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.demandes_sortie import router as demandes_sortie_router
from app.api.documents import router as documents_router
from app.api.documents_fournisseurs import router as documents_fournisseurs_router
from app.api.documents_materiel import router as documents_materiel_router
from app.api.emplacements import router as emplacements_router
from app.api.familles import router as familles_router
from app.api.health import router as health_router
from app.api.inventaires import router as inventaires_router
from app.api.inventaires_avances import router as inventaires_avances_router
from app.api.litiges_fournisseurs import router as litiges_fournisseurs_router
from app.api.lots_beton import router as lots_beton_router
from app.api.magasin import router as magasin_router
from app.api.maintenance_materiel import router as maintenance_materiel_router
from app.api.materiels import router as materiels_router
from app.api.mouvements import router as mouvements_router
from app.api.non_conformites_fournisseurs import router as non_conformites_fournisseurs_router
from app.api.pilotage_achats import router as pilotage_achats_router
from app.api.preparations import router as preparations_router
from app.api.prets_materiel import router as prets_materiel_router
from app.api.reapprovisionnement import router as reapprovisionnement_router
from app.api.receptions_qualite import router as receptions_qualite_router
from app.api.reservations import router_notifications, router_reservations
from app.api.stocks import router as stocks_router
from app.api.utilisateurs import router as utilisateurs_router
from app.api.valorisation import router as valorisation_router

__all__ = [name for name in globals() if name.endswith('_router') or name.startswith('router_')]
