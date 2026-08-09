# Préparations V3 — Lot B : préparation physique

## Fonctions ajoutées

- démarrer une préparation validée ;
- traiter les lignes avec :
  - `✓` complet ;
  - `½` partiel ;
  - `!` indisponible ;
  - `↺` remise à préparer ;
- calcul du manquant ;
- progression globale ;
- passage automatique à `PRETE` lorsque toutes les lignes sont complètes.

## Hors périmètre

- remplacement ;
- expédition ;
- mouvement de stock ;
- décrémentation du stock.

## Installation

Aucune nouvelle migration.

```powershell
docker compose up --build -d backend frontend
```

## Vérifications

```powershell
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

## Recette

1. Créer et valider une préparation.
2. Cliquer sur `Démarrer la préparation`.
3. Marquer une ligne complète.
4. Saisir une quantité partielle et son motif.
5. Déclarer une ligne indisponible.
6. Vérifier le manquant et la progression.
7. Remettre une ligne à préparer.
8. Marquer toutes les lignes complètes.
9. Vérifier le passage à `PRETE`.
10. Vérifier que stock physique et réservations n’ont pas changé.

## Git

```powershell
git status
git add .
git commit -m "feat: add physical preparation workflow"
git push
```
