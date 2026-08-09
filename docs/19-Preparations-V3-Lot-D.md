# Préparations V3 — Lot D

## Endpoint

```text
POST /api/preparations/{preparation_id}/expedier
```

## Règle centrale

Une expédition est une opération atomique.

Le service `executer_mouvement` conserve son comportement historique par
défaut, mais peut déléguer le commit à l’appelant grâce au paramètre
`valider_transaction`.

Le Lot D l’appelle avec `False`, puis effectue un commit unique lorsque toutes
les lignes ont réussi.

## Remplacements

Lorsqu’un remplacement est accepté, la sortie utilise :

- l’article de remplacement ;
- son lot ;
- son emplacement.

La quantité sortie reste la quantité réellement préparée.

## Stock

L’expédition est la seule étape du flux Préparations V3 qui décrémente le
stock physique.
