# Préparations V3 — Lot C

Le remplacement est autorisé uniquement pour une ligne `INDISPONIBLE`.

La demande d’origine reste traçable dans la table
`remplacements_preparation`.

La réservation est transférée dans une transaction unique :

```text
Réserver la nouvelle cible
Libérer l’ancienne cible
Mettre à jour la réservation active
Créer l’historique
Remettre la ligne à préparer
COMMIT
```
