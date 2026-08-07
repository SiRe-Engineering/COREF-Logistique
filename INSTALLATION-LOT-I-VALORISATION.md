# Lot I — Valorisation des stocks matériaux

## Principe

La V1 valorise tous les stocks gérés dans le référentiel `Articles`.
Les modules `Matériels` et `Moules` restent hors de cette valorisation.

## CUMP

Chaque article possède :

```text
cout_unitaire_moyen
dernier_prix_achat
date_maj_cout
```

Une entrée de stock peut renseigner un `prix_unitaire_ht`.

Le nouveau CUMP est :

```text
(ancien stock × ancien CUMP + quantité entrée × prix entrée)
────────────────────────────────────────────────────────────
ancien stock + quantité entrée
```

Les sorties, retours, transferts et ajustements ne recalculent pas le CUMP.

## Historisation

Chaque mouvement conserve :

```text
prix_unitaire_ht
cout_unitaire_applique
valeur_mouvement
```

Cela permettra ensuite de calculer la consommation matière historique par
affaire sans être affecté par les changements futurs du CUMP.

## Stock

Chaque ligne de stock expose :

```text
valeur_physique
valeur_reservee
valeur_disponible
```

## Reprise du stock existant

Après migration, les articles existants ont un CUMP de `0`.

Pour les valoriser immédiatement :

1. ouvrir `Articles` ;
2. ouvrir la référence ;
3. cliquer sur `Définir / corriger le CUMP` ;
4. saisir le coût unitaire actuel.

Les nouvelles entrées avec prix d’achat mettront ensuite le CUMP à jour
automatiquement.

## Tableau de bord

Le dashboard affiche :

- valeur du stock physique ;
- valeur réservée ;
- valeur disponible ;
- valeur des lots béton à échéance dans les 60 jours.

## Migration

```text
0024
```

Prérequis :

```text
0023
```

## Installation

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

Puis :

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Résultat attendu :

```text
0024 (head)
```

## Recette

1. Définir un CUMP initial sur un article déjà en stock.
2. Vérifier la valorisation sur `Stocks` et sur le dashboard.
3. Créer une entrée avec un prix unitaire différent.
4. Vérifier le nouveau CUMP.
5. Créer une sortie.
6. Vérifier que le mouvement conserve le CUMP appliqué et sa valeur.
7. Vérifier qu’une sortie ne modifie pas le CUMP.
8. Vérifier valeur physique = quantité physique × CUMP.
9. Vérifier valeur réservée = quantité réservée × CUMP.
10. Vérifier valeur disponible = disponible × CUMP.

## Git

```powershell
git status
git add .
git commit -m "feat: add weighted average stock valuation"
git push
```
