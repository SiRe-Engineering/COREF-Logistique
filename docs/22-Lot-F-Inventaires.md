# Lot F — Architecture des inventaires

## Campagne

Une campagne possède un périmètre :

```text
EMPLACEMENT
GENERAL
FAMILLE
```

## Ligne

Une ligne est identifiée par :

```text
inventaire
emplacement
article
lot éventuel
```

Le stock théorique est photographié au démarrage. Le comptage peut ensuite
être réalisé sans modifier le stock.

## Validation

La validation est transactionnelle. Tous les ajustements réussissent ou aucun
n’est conservé.

## Traçabilité

Chaque mouvement d’ajustement possède `inventaire_id`.
