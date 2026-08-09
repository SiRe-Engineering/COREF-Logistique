# Correctif AA.1 — Restauration chargement API

## Cause
Le Lot AA ajoutait `Depends(utilisateur_courant)` globalement à tous les routeurs métier.
Or plusieurs écrans historiques utilisent encore des appels `fetch()` sans `Authorization` :
notamment Articles, Stocks et certaines données référentielles d'Achats.

Ces appels recevaient donc `401 Unauthorized`, ce qui produisait :
- `Impossible de charger les données depuis l’API.`
- `Impossible de charger le module Stock.`
- `Impossible de charger le module achats.`

## Correction
AA.1 retire uniquement la protection globale de `main.py`.

Les routes qui possédaient déjà leur propre authentification continuent de la conserver.
Le nettoyage architectural, le menu simplifié et les autres corrections AA restent en place.

Aucune migration.

## Installation
Extraire le correctif à la racine puis :

```powershell
docker compose up --build -d backend
docker compose logs backend --tail=100
curl.exe http://127.0.0.1:8000/api/health
```

Puis :

```powershell
docker compose up -d frontend
```

et `Ctrl + F5`.

## Recette
Tester immédiatement :
1. Articles
2. Stocks
3. Fournisseurs / Achats
4. Dashboard
5. Préparations

## Suite sécurité
La sécurisation complète des API sera reprise proprement dans un lot séparé :
chaque `fetch()` frontend sera authentifié avant de rendre la route backend obligatoire.
