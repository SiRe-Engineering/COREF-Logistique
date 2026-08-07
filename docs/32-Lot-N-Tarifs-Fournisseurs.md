# Lot N — Tarifs fournisseurs

Le Lot N exploite la structure `articles_fournisseurs` créée au Lot M.

## Règles

Un article peut avoir plusieurs fournisseurs mais un seul fournisseur préféré.

Le fournisseur préféré devient la source automatique utilisée par le Lot L
pour proposer :

```text
fournisseur
prix
délai
référence fournisseur
```

Lors de la commande, le tarif du fournisseur sélectionné prime sur le prix
prévisionnel du besoin lorsqu’un tarif est enregistré.

Le minimum de commande fournisseur est également appliqué au moment de créer
la ligne de commande.

## Historisation

Les changements de prix sont conservés dans :

```text
historique_prix_fournisseurs
```

Cette table ne modifie pas le CUMP. Le CUMP reste recalculé uniquement à la
réception physique, selon le prix réellement réceptionné.
