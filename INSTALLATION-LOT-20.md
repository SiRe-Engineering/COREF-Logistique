# Lot 20 — Administration technique des lots et écritures de stock

## Droits

Les actions sont réservées exclusivement au rôle :

```text
ADMINISTRATEUR_TECHNIQUE
```

Le contrôle est appliqué côté interface et côté API.

## Suppression d’un lot

La suppression est une archive auditée :

- le lot disparaît des listes actives ;
- son historique reste conservé ;
- l’auteur, la date et le motif sont enregistrés.

La suppression est refusée si le lot possède :

- du stock physique ;
- du stock réservé ;
- une écriture de stock non annulée ;
- une référence dans une préparation ;
- une référence dans une réservation.

## Suppression d’une écriture de stock

Une écriture n’est pas effacée physiquement. Elle est annulée et son effet est
contre-passé automatiquement :

- entrée / retour / ajustement positif : retrait du stock ;
- sortie / ajustement négatif : réintégration du stock ;
- transfert : retour de la destination vers la source.

L’annulation est refusée si la contre-passation ferait passer le stock
disponible sous zéro ou sous les réservations actives.

## Migration

```text
0020
```

Elle ajoute les champs d’audit aux lots et aux mouvements.

## Installation

Prérequis :

```text
Alembic : 0019
```

Copier l’archive à la racine du projet, puis :

```powershell
docker compose down
docker compose up --build -d
```

Ne pas utiliser `-v`.

## Contrôles

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

Résultat attendu :

```text
0020 (head)
Application startup complete
Ready
```

## Tests fonctionnels

### Lot

1. Se connecter avec `contact@sire-engineering.fr`.
2. Vérifier la présence de l’icône de suppression.
3. Tenter de supprimer un lot avec stock : refus attendu.
4. Ramener stock et réservations à zéro.
5. Annuler les écritures liées.
6. Supprimer le lot avec un motif.
7. Vérifier sa disparition de la liste.

### Mouvement

1. Créer une entrée test de 10 unités.
2. Relever le stock.
3. Annuler l’écriture avec un motif.
4. Vérifier que les 10 unités sont retirées.
5. Créer une sortie test.
6. L’annuler.
7. Vérifier que le stock est réintégré.
8. Tester une annulation impossible à cause d’une réservation active.

### Sécurité

1. Se connecter avec un utilisateur COREF.
2. Vérifier l’absence des boutons.
3. Appeler directement les endpoints avec ce compte.
4. Vérifier la réponse `403`.

## Git

Après validation uniquement :

```powershell
git status
git add .
git commit -m "feat: allow technical admin to cancel stock entries and lots"
git push
```
