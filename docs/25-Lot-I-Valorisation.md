# Lot I — Valorisation matériaux

## Source de coût

Le CUMP est porté par l’article et s’applique à l’ensemble de ses
emplacements et lots.

## Entrées

Seules les entrées accompagnées d’un prix d’achat recalculent le CUMP.

Une entrée sans prix reste autorisée pour compatibilité avec les usages
existants ; elle est valorisée au CUMP courant.

## Sorties et affaires

Le champ `cout_unitaire_applique` est figé dans chaque mouvement. La valeur
d’une sortie vers une affaire est donc historiquement stable.

## Retours

Un retour réintègre une quantité au CUMP courant sans recalculer le coût.
Une version ultérieure pourra réintégrer au coût exact de la sortie d’origine
si une politique comptable différente est retenue.
