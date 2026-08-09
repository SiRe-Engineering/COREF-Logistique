# Lot 11 — Affaires et sorties chantier

## Fonctionnalités

- création des affaires chantier et atelier ;
- référence interne automatique `AFF-000001` ;
- code COREF ou ERP ;
- client, site, zone d’intervention et chargé d’affaires ;
- rattachement obligatoire des sorties à une affaire ;
- possibilité explicite de sortie libre ;
- véhicule renseigné sur la sortie ;
- traçabilité article, lot béton et affaire.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`. Alembic appliquera la migration `0008`.

## Contrôles

```powershell
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Migration attendue :

```text
Running upgrade 0007 -> 0008
```

Ouvrir :

- http://localhost:8000/docs
- http://localhost:3000/affaires
- http://localhost:3000/mouvements

## Test recommandé

1. Créer une affaire :
   - Code : `A26-145`
   - Nom : `Réfection chaudière`
   - Client : `Client test`
   - Site : `Site industriel`
   - Chargé d’affaires : `Jean Dupont`
   - Zone : `Chaudière`
   - Statut : `En cours`
2. Créer une sortie de béton :
   - sélectionner le lot ;
   - sélectionner l’affaire ;
   - renseigner éventuellement le véhicule ;
   - valider.
3. Vérifier que l’historique affiche l’affaire.
4. Vérifier que la sortie est refusée sans affaire et sans case `Sortie libre`.
5. Passer l’affaire au statut `Terminée` via Swagger, puis vérifier qu’une nouvelle sortie est refusée.

## Git

```powershell
git status
git add .
git commit -m "feat: add business cases and job traceability"
git push
```
