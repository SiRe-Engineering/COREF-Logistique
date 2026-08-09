# Lot H — Tableau de bord

Le tableau de bord est calculé à la lecture à partir des données métier
existantes. Il n’introduit donc aucune table d’agrégation ni migration.

## Endpoint

```text
GET /api/dashboard
```

## Stock disponible

```text
quantité physique - quantité réservée
```

Les alertes sont calculées au niveau article en agrégeant tous les
emplacements.

## Péremptions

Seuls les lots actifs, non supprimés et possédant encore du stock physique
sont présentés.

## Préparations

Le retard est déterminé à partir de `date_besoin`. Les lignes partielles,
indisponibles ou avec remplacement proposé sont signalées comme bloquées.

## Limites V1

Les indicateurs sont opérationnels et instantanés. Les tendances historiques,
la rotation, les consommations mensuelles et la valorisation seront ajoutées
dans une version analytique ultérieure.
