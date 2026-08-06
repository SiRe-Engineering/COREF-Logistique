# Préparations V3 — Fondation de réservation

## Transaction de validation

La validation parcourt toutes les lignes et appelle
`synchroniser_reservation_ligne`.

Chaque stock article et chaque stock de lot est verrouillé avec
`SELECT ... FOR UPDATE`.

Le commit n’intervient qu’après le succès de toutes les lignes.

## Disponibilité

```text
Disponible = Quantité physique - Quantité réservée
```

Une réservation est refusée lorsque la quantité demandée dépasse le
disponible de l’article ou, pour un béton, le disponible du lot.

## Modification

Dans ce lot, seule une préparation `BROUILLON` est modifiable. Cela évite
toute divergence entre le besoin enregistré et le stock réservé.

## Suppression

Les réservations sont libérées à partir de la réservation active réellement
enregistrée, puis supprimées par cascade avec la préparation.
