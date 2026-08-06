# Préparations V3 — Lot D : expédition

## Périmètre

Le Lot D termine le cycle principal des préparations :

```text
PRETE
→ expédition atomique
→ EXPEDIEE
```

## Opérations réalisées

Pour chaque ligne préparée :

1. libération de la réservation active ;
2. décrémentation du stock physique article ;
3. décrémentation du stock physique du lot pour un béton ;
4. création d’un mouvement `SORTIE` lié à l’affaire ;
5. passage de la ligne à `EXPEDIEE`.

Après le succès de toutes les lignes :

- la préparation passe à `EXPEDIEE` ;
- `date_expedition` est renseignée ;
- une notification est créée.

## Atomicité

Le service de mouvements accepte désormais :

```python
valider_transaction=False
```

Pendant une expédition, aucun mouvement ne fait de commit isolé.

Une seule transaction contient :

```text
libération des réservations
toutes les sorties de stock
tous les mouvements
statuts des lignes
statut de la préparation
notification
```

Si une ligne échoue, l’ensemble est annulé.

## Protections

- préparation autre que `PRETE` : refus ;
- préparation déjà expédiée : refus ;
- ligne non préparée : refus ;
- quantité préparée nulle : refus ;
- emplacement source absent : refus ;
- stock physique insuffisant : refus ;
- lot béton absent ou insuffisant : refus ;
- double expédition impossible.

## Quantité expédiée

La quantité sortie est toujours :

```text
quantite_preparee
```

Elle peut donc être différente du besoin initial si la règle métier autorise
ultérieurement une préparation partielle prête.

## Migration

Aucune nouvelle migration.

## Installation

Copier l’archive à la racine de la branche, puis :

```powershell
docker compose up --build -d backend frontend
```

## Contrôles

```powershell
docker compose exec backend alembic current
curl.exe http://127.0.0.1:8000/api/health
docker compose logs backend --tail=150
docker compose logs frontend --tail=100
```

## Recette fonctionnelle

### Expédition standard

1. Créer une préparation.
2. Valider et réserver.
3. Démarrer.
4. Marquer toutes les lignes complètes.
5. Relever :
   - stock physique ;
   - stock réservé ;
   - stock des lots ;
   - nombre de mouvements.
6. Cliquer sur `Expédier`.
7. Vérifier :
   - statut `EXPEDIEE` ;
   - lignes `EXPEDIEE` ;
   - stock physique décrémenté ;
   - stock réservé libéré ;
   - stock du lot décrémenté ;
   - un mouvement `SORTIE` par ligne.

### Double expédition

1. Ouvrir une préparation expédiée.
2. Vérifier l’absence du bouton.
3. Appeler directement l’endpoint.
4. Vérifier la réponse `409`.

### Rollback

1. Préparer plusieurs lignes.
2. Créer volontairement une incohérence de stock sur la dernière.
3. Expédier.
4. Vérifier le refus.
5. Vérifier qu’aucune ligne précédente n’a été sortie.
6. Vérifier que la préparation reste `PRETE`.

## Git après validation

```powershell
git status
git add .
git commit -m "feat: add atomic preparation shipment"
git push
```
