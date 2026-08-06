# Lot 18.3B — Transfert atomique des réservations

## Comportement

### Proposition ou refus

La réservation initiale reste inchangée.

### Acceptation

- le stock du remplacement est contrôlé ;
- la nouvelle quantité est réservée ;
- l’ancienne réservation est libérée ;
- la réservation de la ligne est déplacée vers le remplacement ;
- l’ensemble est validé dans une transaction unique.

En cas d’échec, le rollback conserve la réservation initiale.

## Corrections associées

- la libération suit la réservation réellement active ;
- après acceptation, la ligne revient à `A_PREPARER` ;
- l’expédition utilise l’article, le lot et l’emplacement de remplacement ;
- l’article demandé reste conservé pour la traçabilité.

## Installation

Prérequis :

```text
Lot 18.3A installé
Alembic : 0019
```

Aucune migration supplémentaire.

```powershell
docker compose up --build -d backend frontend
```

## Tests

1. Relever les réservations avant acceptation.
2. Accepter avec stock suffisant.
3. Vérifier :
   - réservation initiale à zéro ;
   - remplacement réservé ;
   - ligne à préparer.
4. Tester avec stock insuffisant.
5. Vérifier que la réservation initiale reste présente.
6. Refuser une proposition et vérifier l’absence de changement.
7. Marquer le remplacement complet, préparer puis expédier.
8. Vérifier que le mouvement de sortie porte sur le remplacement.

## Git

```powershell
git status
git add .
git commit -m "feat: transfer reservations to accepted replacements"
git push
```
