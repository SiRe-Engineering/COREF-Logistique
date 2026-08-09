# Lot I-B — Historique de valorisation

## Pourquoi un snapshot ?

Le CUMP actuel permet de valoriser le stock présent, mais ne permet pas de
reconstituer fidèlement une valeur passée une fois le coût modifié.

COREF Logistique conserve donc une photographie agrégée du mois courant.

## Granularité

La V1 historise la valeur globale par mois.

La répartition par famille est calculée en temps réel. Si un historique par
famille devient nécessaire, le même principe pourra être étendu sans modifier
le modèle actuel.

## Déclenchement

Le snapshot est recalculé après les opérations susceptibles de modifier la
valeur :

```text
mouvement
annulation
CUMP
stock direct
remise à zéro
```

L’ouverture de la page garantit aussi l’existence du snapshot courant.

## Lecture

`GET /api/valorisation`

renvoie :

```text
resume
historique
familles
```
