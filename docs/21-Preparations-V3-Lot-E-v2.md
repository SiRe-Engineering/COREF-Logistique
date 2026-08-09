# Lot E v2 — Source de vérité des retours

## Ligne de préparation

```text
quantite_preparee
quantite_expediee
quantite_retournee
```

- `quantite_preparee` : quantité physiquement préparée ;
- `quantite_expediee` : quantité réellement sortie ;
- `quantite_retournee` : cumul des retours validés.

## Mouvement

Le mouvement conserve la trace de chaque sortie et de chaque retour, mais
n’est plus nécessaire pour calculer la quantité encore retournable.

## Atomicité

Le mouvement `RETOUR` et l’augmentation de `quantite_retournee` sont validés
dans la même transaction.
