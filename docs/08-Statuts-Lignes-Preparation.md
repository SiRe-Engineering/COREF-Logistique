# Règles métier — Exécution d’une ligne de préparation

## États

### À préparer

Aucune quantité n’est préparée.

### Préparée

La quantité préparée est égale à la quantité demandée.

### Partielle

La quantité préparée est strictement supérieure à zéro et strictement
inférieure à la quantité demandée. Un motif est obligatoire.

### Indisponible

La quantité préparée est zéro. Un motif est obligatoire.

## Réinitialisation

L’action `Remettre à préparer` :

- remet la quantité préparée à zéro ;
- recalcule la quantité manquante ;
- efface le motif d’écart ;
- ne modifie pas la réservation du besoin.

## Clôture de la préparation

Une préparation ne peut être marquée prête que lorsque toutes ses lignes sont
au statut `PREPAREE`.
