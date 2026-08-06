# Lot 19 — Cohérence des stocks béton

## Fonctionnement

Pour un article non béton :

```text
Article + emplacement + quantité
```

Pour un béton :

```text
Article + lot obligatoire + emplacement + quantité du lot
```

Le stock global de l’article est ajusté uniquement du delta du lot.

Exemple :

```text
LOT1 : 200 → 150 kg
Delta : -50 kg
Stock article : 475 → 425 kg
```

Ajouter un nouveau lot à 100 kg augmente le stock article de 100 kg.

## Invariant

```text
Stock article dans l’emplacement
=
Somme des stocks de tous les lots de cet article dans l’emplacement
```

## Sécurités

- lot obligatoire pour les bétons ;
- lot interdit pour les autres familles ;
- contrôle de correspondance lot/article ;
- impossible de descendre sous le réservé ;
- rollback en cas d’incohérence ;
- aucun double comptage lors de la modification d’un lot existant.

## Installation

Prérequis :

```text
Alembic : 0019
Lots 18.3A et 18.3B installés
```

Aucune migration supplémentaire.

```powershell
docker compose up --build -d backend frontend
```

## Tests fonctionnels

1. Définir 200 kg de Criterion 80E sur LOT1 au Magasin Principal.
2. Valider une préparation demandant LOT1.
3. Vérifier que la réservation fonctionne.
4. Modifier LOT1 de 200 à 150 kg.
5. Vérifier que le stock article baisse seulement de 50 kg.
6. Ajouter LOT2 à 100 kg.
7. Vérifier que le stock article augmente de 100 kg.
8. Vérifier que la somme des lots égale le stock article.
9. Tester une quantité inférieure au réservé : l’opération doit être refusée.

## Attention aux stocks historiques

Si un stock béton global existait avant ce lot sans ligne `StockLot`, il faut
le réaffecter à ses vrais lots avec le formulaire. Le système refusera toute
incohérence entre le total article et la somme des lots.

## Git

```powershell
git status
git add .
git commit -m "fix: synchronize concrete article and batch stocks"
git push
```
