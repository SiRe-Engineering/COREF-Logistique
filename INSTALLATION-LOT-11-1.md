# Lot 11.1 — Édition des affaires

## Fonctionnalités

- lignes d’affaires cliquables ;
- panneau latéral de consultation ;
- formulaire d’édition ;
- modification du statut ;
- modification du client, site, zone et chargé d’affaires ;
- modification des dates et du commentaire ;
- mise à jour immédiate de la liste.

## Installation

Ce lot ne modifie ni la base de données ni le backend.

Copier les deux fichiers suivants à la racine du projet :

- `frontend/app/affaires/page.tsx`
- `frontend/app/affaires/page.module.css`

Puis redémarrer le frontend :

```powershell
docker compose restart frontend
```

Si le rechargement automatique ne suffit pas :

```powershell
docker compose up --build -d frontend
```

## Test

1. Ouvrir `http://localhost:3000/affaires`.
2. Cliquer sur l’affaire `20260001`.
3. Cliquer sur `Modifier l’affaire`.
4. Passer le statut de `En cours` à `Terminée`.
5. Enregistrer.
6. Vérifier que le badge est mis à jour.
7. Vérifier qu’une nouvelle sortie sur cette affaire est ensuite refusée.

## Git

```powershell
git status
git add frontend/app/affaires
git commit -m "feat: add business case editing"
git push
```
