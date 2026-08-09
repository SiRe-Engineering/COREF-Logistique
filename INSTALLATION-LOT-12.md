# Lot 12 — Gestion du matériel

## Fonctionnalités

- numéro d’inventaire automatique `MAT-000001` ;
- catégories de matériel ;
- marque, modèle et numéro de série ;
- état du matériel ;
- localisation ;
- affectation à une affaire ;
- date et valeur d’achat ;
- suivi du dernier et du prochain contrôle ;
- alertes à trente jours ;
- création et édition depuis l’interface.

## Installation

```powershell
docker compose down
```

Copier tous les fichiers du lot à la racine du dépôt, puis :

```powershell
docker compose up --build -d
```

Ne pas utiliser `-v`. Alembic appliquera la migration `0009`.

## Contrôles

```powershell
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Migration attendue :

```text
Running upgrade 0008 -> 0009
```

Ouvrir :

- http://localhost:8000/docs
- http://localhost:3000/materiels

## Test recommandé

Créer :

```text
Désignation : Malaxeur 50 L
Catégorie : Malaxeur
Marque : Collomix
Modèle : XM2
Numéro de série : TEST-0001
État : Disponible
Emplacement : Magasin Principal
Dernier contrôle : 01/08/2026
Prochain contrôle : 01/08/2027
Type : Vérification électrique annuelle
```

Puis :

1. cliquer sur la ligne ;
2. modifier l’état en `En chantier` ;
3. sélectionner l’affaire `20260001` ;
4. enregistrer ;
5. vérifier l’affectation dans le tableau ;
6. tenter `En chantier` sans affaire : l’opération doit être refusée.

## Git

```powershell
git status
git add .
git commit -m "feat: add equipment register"
git push
```
