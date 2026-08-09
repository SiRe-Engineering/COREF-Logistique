# Lot AB.2 — Sécurisation progressive frontend/backend

## Principe

AB.2 ne répète pas la protection globale du Lot AA.

Le correctif commence par convertir les appels HTTP côté frontend vers un wrapper
`apiFetch()` qui ajoute automatiquement le jeton de session sans écraser les
headers existants.

Ensuite seulement, les API historiques du noyau V1 sont protégées :

- Articles
- Stocks
- Emplacements
- Familles
- Affaires
- Lots béton
- Matériels
- Mouvements

Les modules récents qui possèdent déjà `utilisateur_courant` ne sont pas modifiés.

## Frontend

`frontend/lib/api.ts` centralise désormais l'authentification HTTP.

Fichiers frontend convertis automatiquement : **33**.

`AuthProvider.tsx` reste volontairement sur `fetch()` brut car il gère lui-même
login, logout et `/api/auth/me`.

## Backend

La protection est déclarée directement sur les 8 `APIRouter`, donc elle s'applique
également si une nouvelle route est ajoutée dans ces modules.

Les suppressions déjà réservées à l'administrateur technique conservent leur
contrôle de rôle plus strict.

## Installation

Extraire à la racine puis :

```powershell
powershell -ExecutionPolicy Bypass -File .\APPLIQUER-ET-VERIFIER-LOT-AB2.ps1
```

Attendu :

```text
0038 (head)
MAPPERS : OK
```

La suite de tests doit rester entièrement verte. Le nombre augmente d'un test
avec `test_ab2_route_security.py`.

Les appels anonymes :

```text
GET /api/articles
GET /api/stocks
```

doivent répondre `401 Unauthorized`.

## Recette navigateur obligatoire

Après `Ctrl + F5`, se connecter puis tester :

1. Dashboard
2. Articles : liste, création, modification
3. Stocks : liste et actions
4. Emplacements
5. Affaires
6. Lots béton
7. Matériels
8. Mouvements
9. Préparations
10. Fournisseurs / Achats
11. Inventaires
12. Alertes

L'objectif est que la sécurité backend soit renforcée **sans aucune régression
fonctionnelle**.
