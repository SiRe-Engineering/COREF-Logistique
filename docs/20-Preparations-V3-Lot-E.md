# Préparations V3 — Lot E

## Endpoints

```text
GET  /api/preparations/{id}/retours/disponibles
POST /api/preparations/{id}/retours
```

## Source de vérité

Les quantités retournables sont calculées à partir des mouvements :

```text
SORTIE liée à la préparation et à la ligne
moins
RETOUR lié à la même préparation et à la même ligne
```

Aucune quantité cumulée supplémentaire n’est stockée.

## Retour béton

Le mouvement de retour reprend le lot réellement expédié. Le stock global de
l’article et le stock du lot sont augmentés dans le même traitement.

## Préparation

La préparation reste au statut `EXPEDIEE`. Le retour est un nouveau mouvement
logistique ; il ne réouvre pas la préparation.
