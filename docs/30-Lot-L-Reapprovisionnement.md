# Lot L — Réapprovisionnement

Le Lot L reste volontairement un module logistique et non un ERP achats.

Il répond à trois questions :

1. Qu'est-ce qu'il faut réapprovisionner ?
2. Qu'est-ce qui a été validé / commandé ?
3. Qu'est-ce qui a réellement été reçu en stock ?

La réception réutilise `executer_mouvement()`. Cela évite une seconde logique
de stock et garantit que valorisation, CUMP, lots béton et snapshots restent
cohérents.

Le fournisseur reste un champ libre dans cette V1. Un référentiel fournisseurs
et de vraies commandes multi-lignes pourront constituer le lot suivant.
