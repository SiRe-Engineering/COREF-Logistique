# Règles métier — COREF Logistique

## Réservations

- Le champ réservé du stock n’est jamais saisi manuellement.
- Chaque quantité réservée doit correspondre à une réservation identifiable.
- Une réservation indique qui réserve, pour quelle préparation et pour quelle affaire.
- La validation d’une préparation crée les réservations.
- Une modification d’une préparation validée ou en cours synchronise immédiatement
  les quantités réservées.
- La suppression d’une ligne libère sa réservation.
- L’expédition libère la réservation avant de créer la sortie de stock.
- Une quantité physique ne peut pas être abaissée sous le total des réservations actives.
- Les réservations historiques existantes sont reprises avec le motif
  `Reprise historique`.

## Préparations

- Une préparation reste éditable aux statuts Brouillon, Validée et En préparation.
- Les informations générales, les quantités, les lots et les emplacements peuvent
  être modifiés tant que la préparation n’est pas prête.
- Les lignes peuvent être ajoutées ou supprimées pendant ces statuts.
- Une préparation prête ou expédiée est figée.

## Notifications

- Le demandeur reçoit une notification lors de la création, de la réservation,
  du démarrage, de la mise à disposition et de l’expédition.
- Le préparateur reçoit les mêmes notifications lorsqu’il est différent du demandeur.
- Une nouvelle attribution génère une notification au nouvel utilisateur.
- Les notifications sont nominatives et affichées dans le tableau de bord.
- En attendant le module d’authentification, l’utilisateur courant est sélectionné
  dans le tableau de bord et mémorisé localement dans le navigateur.
