# Remise à zéro technique

Endpoint :

```text
POST /api/stocks/{stock_id}/remise-a-zero
```

La remise à zéro est atomique. En cas d’erreur, aucune modification n’est
validée.

Elle est destinée à remettre en cohérence une situation historique avant de
ressaisir les stocks réels lot par lot.
