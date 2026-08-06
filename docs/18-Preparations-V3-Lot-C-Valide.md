# Lot C — Flux de remplacement retenu

Le Lot C utilise les champs de remplacement déjà présents sur
`LignePreparation`.

## Proposition

Une ligne indisponible reçoit :

```text
article_remplacement_id
lot_remplacement_id
emplacement_remplacement_id
quantite_remplacement
commentaire_remplacement
propose_par
date_proposition_remplacement
```

Elle passe à `REMPLACEMENT_PROPOSE`.

## Décision

Le remplacement peut être accepté ou refusé.

En cas d’acceptation, `transferer_reservation_remplacement` :

1. contrôle et réserve la nouvelle cible ;
2. libère l’ancienne cible ;
3. met à jour la réservation active ;
4. conserve la proposition et la décision sur la ligne ;
5. remet la ligne à `A_PREPARER`.

L’opération est transactionnelle et ne modifie pas le stock physique.
