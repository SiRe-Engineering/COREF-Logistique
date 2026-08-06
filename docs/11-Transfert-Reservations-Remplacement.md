# Transfert de réservation d’un remplacement accepté

La réservation active d’une ligne représente toujours l’article réellement
réservé. Lors d’une acceptation, ses champs article, lot, emplacement et
quantité sont remplacés dans une transaction unique.

L’acceptation est une décision métier, pas une confirmation de prélèvement.
La ligne revient donc à `A_PREPARER`.

À l’expédition, une décision `ACCEPTEE` entraîne une sortie sur la référence
de remplacement.
