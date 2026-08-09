# Lot AB — Sécurisation V1

## Résultat de l'audit statique

- Appels `fetch()` frontend recensés : **148**
- Appels sans authentification détectable à proximité : **53**
- Modules API recensés : **32**
- Modules utilisant déjà `utilisateur_courant` : **21**

Le Lot AA a montré qu'une protection globale immédiate casse encore des écrans historiques.
AB commence donc par une cartographie précise avant verrouillage.

## Fetch frontend à vérifier / convertir

- `frontend/app/page.tsx` → ``${API}/api/maintenance-materiel/dashboard``
- `frontend/app/page.tsx` → ``${API}/api/notifications/me``
- `frontend/components/auth/AuthProvider.tsx` → ``${API_URL}/api/auth/login``
- `frontend/app/materiels/page.tsx` → ``${API_URL}/api/materiels``
- `frontend/app/materiels/page.tsx` → ``${API_URL}/api/emplacements?racines_uniquement=false``
- `frontend/app/materiels/page.tsx` → ``${API_URL}/api/affaires``
- `frontend/app/materiels/page.tsx` → ``${API_URL}/api/materiels``
- `frontend/app/materiels/page.tsx` → ``${API_URL}/api/materiels/${materielSelectionne.id}``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/stocks``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/emplacements?racines_uniquement=false``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/stocks/resume``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/reservations?article_id=${stock.article_id}` +`
- `frontend/app/stocks/page.tsx` → ``${API_URL}/api/stocks``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/mouvements``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/emplacements?racines_uniquement=false``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/affaires``
- `frontend/app/mouvements/page.tsx` → ``${API_URL}/api/mouvements``
- `frontend/app/emplacements/page.tsx` → ``${API_URL}/api/emplacements``
- `frontend/app/emplacements/page.tsx` → ``${API_URL}/api/emplacements``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/preparations``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/affaires``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/emplacements?racines_uniquement=false``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/preparations``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/preparations/${selection.id}``
- `frontend/app/preparations/page.tsx` → `url`
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}``
- `frontend/app/preparations/page.tsx` → ``${API_URL}/api/preparations/${selection.id}/lignes/${ligne.id}``
- `frontend/app/reapprovisionnement/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/affaires/page.tsx` → ``${API_URL}/api/affaires``
- `frontend/app/affaires/page.tsx` → ``${API_URL}/api/affaires``
- `frontend/app/affaires/page.tsx` → ``${API_URL}/api/affaires/${affaireSelectionnee.id}``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/familles``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/articles/${articleSelectionne.id}``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/articles/${article.id}``
- `frontend/app/articles/page.tsx` → ``${API_URL}/api/articles/${article.id}``
- `frontend/app/lots-beton/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/lots-beton/page.tsx` → ``${API_URL}/api/articles``
- `frontend/app/lots-beton/page.tsx` → ``${API_URL}/api/lots-beton``
- `frontend/app/achats/page.tsx` → ``${API}/api/lots-beton``
- `frontend/app/lots-beton/[id]/etiquette/page.tsx` → ``${API_URL}/api/lots-beton/${params.id}``
- `frontend/app/articles/[id]/etiquette/page.tsx` → ``${API_URL}/api/articles/${params.id}``
- `frontend/app/inventaires/[id]/impression/page.tsx` → ``${API_URL}/api/inventaires/${params.id}``
- `frontend/app/preparations/[id]/expedition/page.tsx` → ``${API_URL}/api/preparations/${params.id}``
- `frontend/app/preparations/[id]/impression/page.tsx` → ``${API_URL}/api/preparations/${params.id}``
- `frontend/app/preparations/[id]/retour/page.tsx` → ``${API_URL}/api/preparations/${params.id}``

## Matrice backend

- `backend/app/api/preparations.py` — 17 route(s) — **déjà authentifié**
- `backend/app/api/alertes.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/documents_fournisseurs.py` — 5 route(s) — **déjà authentifié**
- `backend/app/api/inventaires.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/mouvements.py` — 3 route(s) — **à auditer**
- `backend/app/api/materiels.py` — 3 route(s) — **à auditer**
- `backend/app/api/magasin.py` — 1 route(s) — **déjà authentifié**
- `backend/app/api/demandes_sortie.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/inventaires_avances.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/documents_materiel.py` — 5 route(s) — **déjà authentifié**
- `backend/app/api/achats.py` — 12 route(s) — **déjà authentifié**
- `backend/app/api/pilotage_achats.py` — 2 route(s) — **déjà authentifié**
- `backend/app/api/articles.py` — 5 route(s) — **à auditer**
- `backend/app/api/prets_materiel.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/utilisateurs.py` — 4 route(s) — **à auditer**
- `backend/app/api/receptions_qualite.py` — 1 route(s) — **déjà authentifié**
- `backend/app/api/lots_beton.py` — 5 route(s) — **à auditer**
- `backend/app/api/emplacements.py` — 4 route(s) — **à auditer**
- `backend/app/api/alertes_logistiques.py` — 1 route(s) — **déjà authentifié**
- `backend/app/api/documents.py` — 1 route(s) — **à auditer**
- `backend/app/api/reapprovisionnement.py` — 5 route(s) — **déjà authentifié**
- `backend/app/api/valorisation.py` — 1 route(s) — **déjà authentifié**
- `backend/app/api/affaires.py` — 4 route(s) — **à auditer**
- `backend/app/api/familles.py` — 8 route(s) — **à auditer**
- `backend/app/api/health.py` — 1 route(s) — **à auditer**
- `backend/app/api/non_conformites_fournisseurs.py` — 3 route(s) — **déjà authentifié**
- `backend/app/api/maintenance_materiel.py` — 4 route(s) — **déjà authentifié**
- `backend/app/api/litiges_fournisseurs.py` — 7 route(s) — **déjà authentifié**
- `backend/app/api/auth.py` — 3 route(s) — **déjà authentifié**
- `backend/app/api/stocks.py` — 4 route(s) — **à auditer**
- `backend/app/api/dashboard.py` — 1 route(s) — **déjà authentifié**
- `backend/app/api/reservations.py` — 3 route(s) — **déjà authentifié**